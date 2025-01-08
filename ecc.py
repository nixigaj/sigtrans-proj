import numpy as np


class FrameSynchronizer:
    def __init__(self, sync_pattern=b'\xAA\xAA', max_bit_errors=1):
        self.sync_pattern = sync_pattern
        self.sync_len = len(sync_pattern)
        self.max_bit_errors = max_bit_errors

    def prepare_frame(self, data):
        """
        Prepare data for transmission by adding sync pattern and length.
        """
        # Convert length to 2 bytes
        length = len(data).to_bytes(2, byteorder='big')

        # Calculate simple checksum
        checksum = sum(data) & 0xFF
        checksum_byte = bytes([checksum])

        # Construct frame: SYNC + LENGTH + DATA + CHECKSUM
        frame = self.sync_pattern + length + data + checksum_byte
        return frame

    def count_bit_differences(self, byte1, byte2):
        """
        Count the number of different bits between two bytes.
        """
        xor = byte1 ^ byte2
        return bin(xor).count('1')

    def find_sync_pattern(self, buffer):
        """
        Find the sync pattern in the received buffer, allowing for bit errors.
        Returns the index of the start of the sync pattern, or -1 if not found.
        """
        buffer_len = len(buffer)
        pattern_len = len(self.sync_pattern)

        for i in range(buffer_len - pattern_len + 1):
            total_bit_errors = 0
            is_match = True

            for j in range(pattern_len):
                bit_errors = self.count_bit_differences(buffer[i + j], self.sync_pattern[j])
                total_bit_errors += bit_errors

                if total_bit_errors > self.max_bit_errors:
                    is_match = False
                    break

            if is_match:
                return i
        return -1

    def recover_frame(self, received_buffer, min_frame_size=5):
        """
        Attempt to recover a valid frame from the received buffer.
        Returns (frame, remaining_buffer) if successful, (None, received_buffer) if not.
        """
        if len(received_buffer) < min_frame_size:
            return None, received_buffer

        # Find sync pattern
        sync_index = self.find_sync_pattern(received_buffer)
        if sync_index == -1:
            return None, received_buffer

        # Remove data before sync pattern
        buffer = received_buffer[sync_index:]
        if len(buffer) < min_frame_size:
            return None, received_buffer

        # Read length field (2 bytes after sync pattern)
        try:
            length = int.from_bytes(buffer[self.sync_len:self.sync_len + 2], byteorder='big')
            total_frame_size = self.sync_len + 2 + length + 1  # sync + length + data + checksum

            if len(buffer) < total_frame_size:
                return None, received_buffer

            # Extract the frame
            frame = buffer[:total_frame_size]
            remaining_buffer = buffer[total_frame_size:]

            # Verify checksum with bit error tolerance
            received_checksum = frame[-1]
            calculated_checksum = sum(frame[self.sync_len + 2:-1]) & 0xFF

            checksum_bit_errors = self.count_bit_differences(received_checksum, calculated_checksum)
            if checksum_bit_errors <= self.max_bit_errors:
                return frame, remaining_buffer

        except Exception as e:
            pass

        # If we get here, frame was invalid
        return None, received_buffer[sync_index + 1:]

    def extract_data(self, frame):
        """
        Extract the data portion from a valid frame.
        """
        if frame is None:
            return None
        return frame[self.sync_len + 2:-1]  # Remove sync pattern, length, and checksum


def simulate_transmission_errors(data, bit_error_rate=0.001):
    """
    Simulate random bit errors in transmission.
    """
    data_array = np.frombuffer(data, dtype=np.uint8)
    bit_array = np.unpackbits(data_array)

    # Randomly flip bits
    error_mask = np.random.random(len(bit_array)) < bit_error_rate
    bit_array = np.logical_xor(bit_array, error_mask)

    # Randomly insert or delete bits
    if np.random.random() < 0.1:  # 10% chance of insertion/deletion
        if np.random.random() < 0.5:
            # Insert random bit
            insert_pos = np.random.randint(0, len(bit_array))
            bit_array = np.insert(bit_array, insert_pos, np.random.randint(0, 2))
        else:
            # Delete random bit
            delete_pos = np.random.randint(0, len(bit_array))
            bit_array = np.delete(bit_array, delete_pos)

    # Pad with zeros if necessary to make byte-aligned
    padding = (8 - len(bit_array) % 8) % 8
    if padding:
        bit_array = np.pad(bit_array, (0, padding))

    # Convert back to bytes
    return np.packbits(bit_array).tobytes()


def flip_last_bit(data: bytes) -> bytes:
    """
    Flip the last bit of the last byte in a bytes object.

    Parameters:
        data (bytes): The input bytes object.

    Returns:
        bytes: A new bytes object with the last bit of the last byte flipped.
    """
    if not data:
        raise ValueError("Input bytes object cannot be empty.")

    # Convert to a mutable bytearray
    mutable_data = bytearray(data)

    # Flip the last bit of the last byte
    mutable_data[-1] ^= 0b00000001

    # Convert back to bytes and return
    return bytes(mutable_data)


### Test below ###

def ecc_test():
    # Create a synchronizer that tolerates 1 bit error
    sync = FrameSynchronizer(max_bit_errors=1)

    # Your received data with the flipped bit
    data_rx = bytes([
        int('10101010', 2), int('10101010', 2), int('00000000', 2),
        int('00001101', 2), int('01001000', 2), int('01100101', 2),
        int('01101100', 2), int('01101100', 2), int('01101111', 2),
        int('00101100', 2), int('00100000', 2), int('01110111', 2),
        int('01101111', 2), int('01110010', 2), int('01101100', 2),
        int('01100100', 2), int('00100001', 2), int('10001001', 2)
    ])

    # Try to recover the frame
    recovered_frame, remaining = sync.recover_frame(data_rx)
    if recovered_frame is not None:
        recovered_data = sync.extract_data(recovered_frame)
        print(f"Recovered: {recovered_data.decode()}")

#ecc_test()
