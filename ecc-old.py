import numpy as np

class FrameSynchronizer:
    def __init__(self, sync_pattern=b'\xAA\xAA'):  # Default sync pattern: 10101010 10101010
        self.sync_pattern = sync_pattern
        self.sync_len = len(sync_pattern)

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

    def find_sync_pattern(self, buffer):
        """
        Find the sync pattern in the received buffer.
        Returns the index of the start of the sync pattern, or -1 if not found.
        """
        buffer_len = len(buffer)
        pattern_len = len(self.sync_pattern)

        for i in range(buffer_len - pattern_len + 1):
            if buffer[i:i + pattern_len] == self.sync_pattern:
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

            # Verify checksum
            received_checksum = frame[-1]
            calculated_checksum = sum(frame[self.sync_len + 2:-1]) & 0xFF

            if received_checksum == calculated_checksum:
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


### Test below ###

def ecc_test():
    # Create a synchronizer instance
    sync = FrameSynchronizer()

    # Prepare data for transmission
    original_data = b'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
    frame = sync.prepare_frame(original_data)

    # Simulate transmission with errors
    received_data = simulate_transmission_errors(frame)

    # Recover the frame
    recovered_frame, remaining = sync.recover_frame(received_data)

    # Extract the original data
    if recovered_frame is not None:
        recovered_data = sync.extract_data(recovered_frame)
        print(f"Recovered: {recovered_data}")
    else:
        print("Could not recover")

#ecc_test()
