# BSV Address Generator

A user-friendly Python tool to derive BSV (Bitcoin SV) addresses from extended public keys (xpub) using the official BSV SDK for Python.

## Features

- 🔐 **Secure Address Derivation**: Generate BSV addresses from extended public keys without exposing private keys
- 📁 **Multiple Input Methods**: Enter xpub directly or load from file
- 🛣️ **Flexible Derivation Paths**: Support for standard receiving/change addresses and custom paths
- 💾 **Export Options**: Save generated addresses to timestamped files
- 🎯 **Batch Generation**: Generate multiple addresses at once (1-1000+ addresses)
- ✅ **Input Validation**: Built-in validation for extended public keys
- 🖥️ **CLI Interface**: Easy-to-use command-line interface with guided prompts

## Prerequisites

- Python 3.7 or higher
- Virtual environment (recommended)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd xpub-gen
```

### 2. Create and Activate Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install bsv-sdk
```

## Usage

### Running the Tool
Make sure your virtual environment is activated, then run:

```bash
python main.py
```

### Testing the Tool
For testing purposes, we've included additional files:

- **`example_xpub.txt`**: Contains a sample xpub for safe testing
- **`test_script.py`**: Comprehensive test script with additional features

To run the test script:
```bash
python test_script.py
```

The test script provides options to:
1. Generate new master private keys and xpubs for testing
2. Use the provided example xpub file
3. Input your own xpub for testing  
4. Use existing master private keys
5. Display both addresses and private keys (for testing scenarios)

### Interactive Setup
The tool will guide you through the process:

1. **Choose Input Method**:
   - Enter xpub directly
   - Load xpub from file

2. **Set Number of Addresses**: 
   - Default: 10 addresses
   - Maximum recommended: 1000 (performance warning for larger numbers)

3. **Select Derivation Path**:
   - Standard receiving addresses (`m/0/i`)
   - Standard change addresses (`m/1/i`) 
   - Custom path (e.g., `44/0/0`, `0/0`)

4. **View Results**: Addresses are displayed in a formatted table

5. **Save Option**: Export addresses to timestamped text file

## Example Usage

### Example 1: Basic Usage
```
Enter your extended public key (xpub): xpub6C...
How many addresses would you like to derive? (default: 10): 5
Enter your choice (1, 2, or 3): 1

Deriving 5 addresses...
================================================================================
Index    Derivation Path      Address
================================================================================
0        m/0/0               1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q
1        m/0/1               1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R
...
```

### Example 2: Using File Input
Create a text file with your xpub:
```bash
echo "xpub6C..." > my_xpub.txt
```

Then run the tool and select option 2 to load from file.

## Supported Extended Public Key Formats

- **Mainnet**: `xpub...` (Bitcoin mainnet format)
- **Testnet**: `tpub...` (Bitcoin testnet format)

## Derivation Paths Explained

- **`m/0/i`**: Standard receiving addresses (external chain)
- **`m/1/i`**: Standard change addresses (internal chain)  
- **Custom**: Any valid BIP32 derivation path

Where `i` is the address index (0, 1, 2, ...).

## Output Format

Generated addresses are displayed with:
- **Index**: Sequential number (0, 1, 2, ...)
- **Derivation Path**: Full BIP32 path used
- **Address**: The resulting BSV address

## File Export

When saving addresses, the tool creates a timestamped file containing:
- Generation metadata (timestamp, total count)
- Complete address details (index, path, address)
- Human-readable formatting

Example filename: `bsv_addresses_20241201_143022.txt`

## Error Handling

The tool includes comprehensive error handling for:
- Invalid extended public keys
- File access issues
- Network connectivity problems
- Invalid derivation paths
- Out-of-range indices

## Security Notes

⚠️ **Important Security Considerations:**

- This tool only works with **extended public keys (xpub)**, never private keys
- Extended public keys can derive addresses but cannot spend funds
- Keep your private keys and extended private keys (xprv) secure and never share them
- Generated addresses are for receiving funds only

## Troubleshooting

### Common Issues

**BSV SDK Not Found**
```
Error: BSV SDK not found. Please install it using:
pip install bsv-sdk
```
**Solution**: Make sure your virtual environment is activated and run `pip install bsv-sdk`

**Invalid Extended Public Key**
```
Error processing extended public key: [error details]
```
**Solution**: Verify your xpub format and ensure it's a valid extended public key

**Permission Denied (File Access)**
```
Error: Permission denied reading 'filename.txt'
```
**Solution**: Check file permissions or run with appropriate user privileges

## Technical Details

- **SDK**: Official BSV SDK for Python
- **Derivation**: BIP32 hierarchical deterministic key derivation
- **Address Format**: P2PKH (Pay-to-Public-Key-Hash)
- **Python Version**: 3.7+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the terms specified in the LICENSE file.

## Support

For issues, questions, or contributions, please refer to the project's issue tracker or documentation.
