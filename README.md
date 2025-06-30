# BSV Address Generator

A comprehensive Python tool to derive BSV (Bitcoin SV) addresses from extended public keys (xpub) with advanced amount distribution and batch processing capabilities.

## 🎯 New GUI Interface Available!

The BSV Address Generator now includes a **user-friendly PyQt6 GUI** that makes address generation accessible to all users. Choose between:

- **🖥️ GUI Mode**: Intuitive graphical interface for easy use
- **⌨️ CLI Mode**: Command-line interface for advanced users and automation

### Quick Start - GUI Mode
```bash
make install      # Install all dependencies including PyQt6
make start-gui    # Launch the graphical interface
```

📖 **[Complete GUI Usage Guide](GUI_USAGE_GUIDE.md)** - Detailed instructions for the graphical interface

## Features

- 🔐 **Secure Address Derivation**: Generate BSV addresses from extended public keys without exposing private keys
- 📁 **Multiple Input Methods**: Enter xpub directly or load from file
- 🛣️ **Flexible Derivation Paths**: Support for standard receiving/change addresses and custom paths
- 💰 **Amount Distribution**: Multiple algorithms for distributing BSV amounts across addresses
- 💾 **Export Options**: Save to TXT files and Electrum SV-compatible CSV files
- 📦 **Batch Processing**: Split large address sets into multiple CSV files for enhanced privacy
- 🎯 **Batch Generation**: Generate multiple addresses at once (1-1000+ addresses)
- 🎲 **Smart Randomization**: Advanced algorithms for optimal amount distribution
- ✅ **Input Validation**: Built-in validation for extended public keys and amounts
- 🖥️ **Dual Interface**: Both GUI and CLI interfaces available
- 🔧 **Development Tools**: Integrated linting, formatting, and testing via Makefile

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

**Automated Installation (Recommended):**
```bash
make install
```

**Manual Installation:**
```bash
# Core dependencies
pip install bsv-sdk

# For GUI interface
pip install PyQt6

# For development (optional)
pip install black isort flake8 pylint mypy
```

## Usage

### Choose Your Interface

#### 🖥️ GUI Mode (Recommended for new users)
```bash
make start-gui
```
- User-friendly graphical interface
- Visual feedback and validation
- Easy file loading and saving
- Real-time preview functionality
- Perfect for occasional users

#### ⌨️ CLI Mode (Recommended for automation)
```bash
make run
```
- Command-line interface with guided prompts
- Scriptable and automatable
- Faster for experienced users
- Better for batch operations

### Alternative Running Methods

**Direct Python execution:**
```bash
# CLI mode
python main.py

# GUI mode
python gui.py
```

**Using virtual environment directly:**
```bash
# CLI mode
./venv/bin/python main.py

# GUI mode  
./venv/bin/python gui.py
```

### Development Tools

The project includes a comprehensive Makefile for development tasks:

```bash
# Format code with black and isort
make format

# Run all linters (flake8, pylint, mypy)
make lint

# Check formatting without making changes
make check

# Clean cache files
make clean

# Show available commands
make help
```

### Testing the Tool
For testing purposes, we've included an additional file:

- **`example_xpub.txt`**: Contains a sample xpub for safe testing

## 📦 Distributing the Application

You can create a standalone, single-file executable from this project using **PyInstaller**. This bundles the application and all its dependencies into one file, making it easy to share.

### 1. Install Dependencies
First, ensure you have all project dependencies, including `pyinstaller`, installed:
```bash
make install
```

### 2. Building for Your Current Platform

To create an executable for your current operating system (e.g., Linux), run the following command:
```bash
make build
```
This command will:
- Bundle the entire application into a single file.
- Use the `assets/app_icon.png` as the application icon.
- Place the final executable in a new `dist/` directory.

The resulting file (`dist/BSV_Address_Generator`) can be run on any compatible Linux distribution without needing Python or any dependencies installed.

### 3. Building for Windows (Cross-Platform)

**Important**: You cannot create a Windows `.exe` file from a Linux or macOS environment. You must run the build process on a Windows machine.

To build for Windows:
1.  Clone this repository onto a Windows machine.
2.  Follow the **Installation** steps in this README to set up Python and the virtual environment.
3.  Run the same build command on Windows (in `cmd` or `PowerShell`):
    ```powershell
    # First, activate the virtual environment if you haven't
    .\venv\Scripts\activate

    # Then, run the build command
    pyinstaller --name "BSV_Address_Generator" --onefile --windowed --additional-hooks-dir=./hooks --icon="assets/app_icon.ico" --add-data="assets;assets" gui.py
    ```
This will create a `BSV_Address_Generator.exe` file inside the `dist/` directory, which can be run on other Windows machines. Note the use of a semicolon (`;`) in the `--add-data` path for Windows compatibility.

## Interactive Workflow

The tool guides you through a comprehensive process:

### 1. Address Generation
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

4. **Starting Index**: Continue from previous derivations or start fresh

### 2. File Export Options

**TXT Export**: Save addresses to a timestamped text file with complete derivation information.

**CSV Export**: Create Electrum SV-compatible CSV files with amount distribution.

### 3. Amount Distribution (CSV Mode)

When creating CSV files, choose from three distribution algorithms:

#### Equal Distribution
- **Use Case**: Simple, uniform distribution
- **Behavior**: All addresses receive exactly the same amount
- **Example**: 100 BSV ÷ 10 addresses = 10 BSV each
- **Best For**: Basic splitting, transparent distributions

#### Manual Random Distribution
- **Use Case**: Custom randomization with user-defined bounds
- **Behavior**: Random amounts within specified min/max range
- **User Input**: Define minimum and maximum amounts per address
- **Example**: Min 0.5 BSV, Max 15 BSV per address
- **Best For**: Custom privacy requirements, specific amount ranges

#### Smart Random Distribution 🤖
- **Use Case**: Optimal randomization with automated bounds calculation
- **Behavior**: AI-powered distribution with intelligent bounds
- **Features**:
  - Automatically calculates optimal min/max bounds
  - Prevents excessive amounts to last address
  - Ensures true randomness across all addresses
  - Maintains reasonable variation while respecting constraints
  - Handles dust limit compliance automatically
  - Provides distribution quality analysis
- **Benefits**:
  - No manual bound calculation needed
  - Prevents common distribution pitfalls
  - Optimal privacy through controlled randomization
  - Quality metrics and analysis
- **Best For**: Professional use, large amounts, optimal privacy

### 4. Batch Processing 📦

After creating a CSV, optionally split it into multiple batch files:

#### Features
- **Smart Splitting**: Split based on maximum BSV amount per batch
- **Privacy Enhancement**: Optional address randomization within batches
- **Organized Output**: Main CSV + subdirectory with batch files
- **Complete Traceability**: Batch info file with full statistics

#### Use Cases
- **Large Transactions**: Split 1000 addresses with 100 BSV into batches of max 10 BSV each
- **Operational Security**: Distribute large amounts across multiple files
- **Privacy**: Randomize address order to prevent correlation
- **File Management**: Easier processing of smaller, manageable files

#### Example Workflow
```
1000 addresses, 100 BSV total, max 10 BSV per batch
→ Creates ~10 batch files + 1 info file in subdirectory
→ Each batch: batch_01_9.87654321_BSV.csv, batch_02_10.00000000_BSV.csv, etc.
→ Includes batch_info.txt with complete statistics
```

## Example Usage Scenarios

### Scenario 1: Basic Address Generation
```
Enter your extended public key (xpub): xpub6C...
How many addresses would you like to derive? (default: 10): 5
Enter your choice (1, 2, or 3): 1

✓ Successfully derived 5 addresses!
```

### Scenario 2: Equal Amount Distribution
```
Would you like to create a CSV with amounts for Electrum SV? (y/n): y
Enter total BSV amount to distribute (e.g., 1.5): 10.0
Choose distribution mode:
1. Equal amounts for all addresses
2. Random amounts (manual bounds)  
3. Smart random distribution (recommended)
Enter your choice (1, 2, or 3): 1

✓ Equal distribution: 2.00000000 BSV per address
✓ CSV saved to: bsv_addresses_amounts_20241201_143022.csv
```

### Scenario 3: Smart Random Distribution with Batch Processing
```
Enter your choice (1, 2, or 3): 3

🎯 Smart Random Distribution Benefits:
• Automatically calculates optimal min/max bounds
• Prevents last address from getting excessive amounts
• Ensures true randomness across all addresses
[...]

🤖 Smart random distribution completed!
✓ Bounds used: 0.15000000 - 3.85000000 BSV per address
✓ Target variation: 35.0% of average

Would you like to split this CSV into multiple batch files? (y/n): y
Enter maximum BSV amount per batch file (e.g., 10.0): 15.0
Would you like to randomize address order within batches? (y/n): y

🔄 Creating batch files...
✅ Batch Processing Complete!
✓ Created 7 batch files in subdirectory: bsv_addresses_amounts_20241201_143022_batches_143045
```

## Output Formats

### TXT Files
```
BSV Addresses Derived from Extended Public Key
==================================================
Generated on: 2024-12-01 14:30:22
Total addresses: 10

Index: 0
Path: m/0/0
Address: 1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q
------------------------------
```

### CSV Files (Electrum SV Format)
```
1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q,2.15430000
1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R,1.87234000
...
```

### Batch Files Structure
```
main_file_batches_20241201_143045/
├── batch_info.txt                     # Summary and statistics
├── batch_01_9.87654321_BSV.csv       # First batch
├── batch_02_10.00000000_BSV.csv      # Second batch
└── batch_03_8.12345679_BSV.csv       # Final batch
```

## Supported Extended Public Key Formats

- **Mainnet**: `xpub...` (Bitcoin mainnet format)
- **Testnet**: `tpub...` (Bitcoin testnet format)

## Derivation Paths Explained

- **`m/0/i`**: Standard receiving addresses (external chain)
- **`m/1/i`**: Standard change addresses (internal chain)  
- **Custom**: Any valid BIP32 derivation path

Where `i` is the address index (0, 1, 2, ...).

## Distribution Quality Analysis

The smart random distribution provides detailed quality metrics:

- **Variation Coefficient**: Measures distribution uniformity
- **Bound Compliance**: Percentage of addresses within expected bounds
- **Distribution Accuracy**: Ensures perfect total amount allocation
- **Excessive Address Detection**: Identifies potential privacy issues

## Security Notes

⚠️ **Important Security Considerations:**

- This tool only works with **extended public keys (xpub)**, never private keys
- Extended public keys can derive addresses but cannot spend funds
- Keep your private keys and extended private keys (xprv) secure and never share them
- Generated addresses are for receiving funds only
- **Batch processing enhances privacy** by splitting large transactions
- **Address randomization** provides additional privacy protection
- **Smart distribution** prevents common analysis patterns

## ⚠️ DISCLAIMER OF LIABILITY

**IMPORTANT: READ CAREFULLY BEFORE USING THIS SOFTWARE**

The developers and contributors of this BSV Address Generator tool provide this software "AS IS" without any warranties or guarantees. **WE ARE NOT RESPONSIBLE FOR ANY LOSS OF FUNDS, CRYPTOCURRENCY, OR ANY OTHER DAMAGES** that may result from:

- Use or misuse of this software
- Loss of private keys or extended private keys
- Incorrect address generation or usage
- Security breaches or vulnerabilities
- User error or negligence
- Any technical issues or bugs

**BY USING THIS SOFTWARE, YOU ACKNOWLEDGE AND ACCEPT FULL RESPONSIBILITY FOR:**
- Securing your private keys and sensitive information
- Verifying all generated addresses before use
- Understanding the risks associated with cryptocurrency operations
- Any financial losses that may occur

## 🔒 CRITICAL SECURITY GUIDELINES

### Essential Security Practices

**🚨 NEVER share or expose your private keys (xprv) or seed phrases**
- Private keys control your funds - anyone with access can steal your cryptocurrency
- This tool only needs your extended public key (xpub) - never input private keys
- Store private keys offline, encrypted, and in multiple secure locations

**🔑 Extended Public Key (xpub) Security:**
- While xpubs can't spend funds, they reveal all your receiving addresses
- Sharing xpubs compromises your privacy and transaction history
- Only use xpubs from wallets you fully control
- Never use someone else's xpub or untrusted sources

**💻 Environment Security:**
- Use this tool only on secure, trusted computers
- Avoid public computers, shared systems, or compromised networks
- Keep your operating system and security software updated
- Use antivirus software and firewall protection

**🧪 Testing Protocol:**
- **ALWAYS test with small amounts first** before large transactions
- Verify generated addresses work correctly with test transactions
- Use testnet addresses for development and testing when possible
- Double-check all addresses before sending funds

### Address Verification Best Practices

**✅ Before sending funds to generated addresses:**
1. **Verify the first few addresses** with small test amounts
2. **Compare generated addresses** with your wallet's receive addresses
3. **Check address format** matches Bitcoin SV standards
4. **Confirm you control the private keys** for the derivation path used

**📋 Address Usage Guidelines:**
- Each address should typically be used only once for privacy
- Monitor all generated addresses for incoming transactions  
- Keep detailed records of which addresses you've used
- Use batch processing for enhanced operational security

### Backup and Recovery

**💾 Essential Backups:**
- **Backup your wallet's seed phrase** (12/24 words) securely offline
- **Store backups in multiple locations** (fireproof safe, safety deposit box)
- **Test recovery procedures** before you need them
- **Document your derivation paths** and starting indices

**🔄 Recovery Planning:**
- Know how to restore your wallet from seed phrase
- Understand how to recreate addresses using derivation paths
- Keep copies of this tool or similar software for address regeneration
- Document all custom derivation paths used

### Operational Security

**🛡️ Transaction Security:**
- Use hardware wallets when possible for enhanced security
- Verify transaction details carefully before broadcasting
- Use appropriate transaction fees to ensure timely confirmation
- Be aware of dust limits and minimum transaction amounts

**🔐 Privacy Protection:**
- Use different addresses for different purposes
- Consider using mixing services for enhanced privacy
- Be cautious about address reuse and transaction linking
- Use batch processing to obscure transaction patterns

**⚠️ Red Flags - Stop and Investigate:**
- Unexpected address formats or patterns
- Addresses that don't match your wallet's generated addresses
- Requests to share private keys or seed phrases
- Pressure to make urgent transactions
- Unsolicited offers or "investment opportunities"

### Emergency Procedures

**🚨 If you suspect compromise:**
1. **Immediately move funds** from potentially compromised addresses
2. **Generate new addresses** using a secure, clean system
3. **Review transaction history** for unauthorized activities
4. **Consider professional security consultation** for large amounts

**📞 When to Seek Help:**
- If you're unsure about any security aspect
- Before handling large amounts of cryptocurrency
- If you discover potential security issues
- When implementing new security procedures

---

**Remember: Cryptocurrency transactions are irreversible. Take security seriously and never risk more than you can afford to lose.**

## Privacy Features

### Enhanced Privacy Through:
- **Batch Processing**: Split large amounts across multiple files
- **Address Randomization**: Shuffle addresses to prevent correlation
- **Smart Amount Distribution**: Avoid predictable patterns
- **Variable Batch Sizes**: Prevent easy batch identification

### Best Practices:
1. Use smart random distribution for optimal privacy
2. Enable batch processing for large amounts (>10 BSV)
3. Use address randomization in random modes
4. Set reasonable maximum batch sizes (5-20 BSV)
5. Process batches independently and at different times

## Error Handling

The tool includes comprehensive error handling for:
- Invalid extended public keys
- Invalid amount inputs and distribution parameters
- File access issues
- Network connectivity problems
- Invalid derivation paths
- Out-of-range indices
- Batch processing errors

## Troubleshooting

### Common Issues

**BSV SDK Not Found**
```bash
pip install bsv-sdk
```

**Make Command Not Found**
```bash
# Install make on Ubuntu/Debian:
sudo apt-get install make

# Install make on macOS:
xcode-select --install
```

**Permission Denied (File Access)**
Check file permissions or run with appropriate user privileges.

**Distribution Errors**
Ensure total amount is greater than minimum required amount and number of addresses.

## Technical Details

- **SDK**: Official BSV SDK for Python
- **Derivation**: BIP32 hierarchical deterministic key derivation
- **Address Format**: P2PKH (Pay-to-Public-Key-Hash)
- **Distribution Algorithms**: Equal, Manual Random, Smart Random with quality analysis
- **File Formats**: TXT (human-readable), CSV (Electrum SV compatible)
- **Batch Processing**: Intelligent splitting with privacy features
- **Python Version**: 3.7+
- **Code Quality**: Black formatting, isort imports, flake8/pylint/mypy linting

## Project Structure

```
xpub-gen/
├── main.py                    # Main application entry point
├── config.py                  # Configuration constants
├── Makefile                   # Development tools
├── bsv_address_generator/     # Core package
│   ├── core/                  # Core logic
│   │   ├── derivation.py      # Address derivation
│   │   └── distribution.py    # Amount distribution algorithms
│   ├── ui/                    # User interface
│   │   ├── input_handlers.py  # Input validation and prompts
│   │   └── output_handlers.py # Display and file operations
│   └── utils/                 # Utilities
│       └── state_manager.py   # State management
└── former_application_files/  # Legacy files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the coding standards:
   ```bash
   make format  # Format code
   make lint    # Run linters
   make test    # Run tests
   ```
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the terms specified in the LICENSE file.

## Support

For issues, questions, or contributions, please refer to the project's issue tracker or documentation.
