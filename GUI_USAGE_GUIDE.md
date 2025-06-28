# BSV Address Generator - GUI Usage Guide

## Overview

The BSV Address Generator now includes a user-friendly PyQt6 graphical interface that provides the same functionality as the command-line version but with an intuitive visual interface.

## Installation & Setup

### 1. Install Dependencies

```bash
make install
```

This will:
- Create/update the virtual environment
- Install all required dependencies including PyQt6
- Set up the development tools

### 2. Launch the GUI

```bash
make start-gui
```

Or alternatively:
```bash
./venv/bin/python gui.py
```

## GUI Interface Overview

The GUI is organized into two main panels:

### Left Panel: Input Controls
1. **Extended Public Key (XPUB)**
   - Large text field for pasting your xpub
   - 📋 Paste button - paste from clipboard
   - 📁 Load from File button - load xpub from text file
   - 🗑️ Clear button - clear the input field

2. **Number of Addresses**
   - Spinner control (1-10,000 addresses)
   - Default: 10 addresses

3. **Derivation Path**
   - Dropdown with common options:
     - Standard receiving (m/0/i)
     - Standard change (m/1/i)
     - Custom path (shows text input for custom paths)

4. **BSV Distribution**
   - Total BSV amount (decimal input with 8-digit precision)
   - Distribution mode dropdown:
     - **Equal distribution**: Same amount for all addresses
     - **Random distribution**: Random amounts within specified bounds
     - **Smart random distribution**: Optimally calculated random bounds

5. **Action Buttons**
   - 🔍 **Preview Distribution**: Shows distribution parameters without generating addresses
   - 🚀 **Generate Addresses**: Starts the address generation process

### Right Panel: Results
Two tabs for viewing results:

1. **📊 Preview Tab**
   - Shows distribution parameters and calculations
   - Helps you understand what will happen before generation

2. **📍 Addresses Tab**
   - Table showing generated addresses with amounts
   - Export buttons:
     - 💾 **Save TXT**: Addresses only (compatible with original format)
     - 📊 **Save CSV**: Addresses with amounts
     - 📦 **Batch Export**: Split into multiple files

## Step-by-Step Usage

### Basic Address Generation

1. **Enter/Load XPUB**
   - Paste your extended public key into the text field
   - Or click "Load from File" to load from a `.txt` file
   - The example xpub will be loaded automatically if available

2. **Set Parameters**
   - Choose number of addresses (default: 10)
   - Select derivation path (default: standard receiving)
   - Enter total BSV amount to distribute

3. **Choose Distribution Mode**
   - **Equal**: All addresses get the same amount
   - **Random**: Specify min/max bounds manually
   - **Smart Random**: Let the system calculate optimal bounds

4. **Preview (Optional)**
   - Click "Preview Distribution" to see calculations
   - Review the parameters in the Preview tab

5. **Generate**
   - Click "Generate Addresses"
   - Wait for generation to complete
   - View results in the Addresses tab

6. **Export Results**
   - Choose your preferred export format
   - Save to desired location

### Advanced Features

#### Smart Random Distribution
- Automatically calculates optimal min/max bounds
- Ensures proper distribution without excessive remainders
- Provides detailed statistics about the distribution

#### Batch Export
- Splits large distributions into smaller files
- Useful for processing in smaller chunks
- Maintains privacy through randomization
- Prompts for maximum BSV per batch file

#### State Management
- Remembers previous derivation states
- Offers to continue from where you left off
- Prevents accidental re-use of addresses

## Distribution Modes Explained

### Equal Distribution
- **Use case**: When you want identical amounts for all addresses
- **Calculation**: Total BSV ÷ Number of addresses
- **Note**: Any remainder goes to the first address

### Random Distribution
- **Use case**: When you want varied amounts for privacy
- **Parameters**: You specify minimum and maximum amounts
- **Validation**: Ensures distribution is mathematically possible
- **Auto-adjustment**: GUI suggests reasonable bounds

### Smart Random Distribution
- **Use case**: Optimal random distribution without manual calculation
- **Algorithm**: Calculates optimal bounds automatically
- **Benefits**: 
  - True randomness across all addresses
  - No excessive remainder for last address
  - Reasonable variation in amounts
  - Compliance with dust limits

## File Formats

### TXT Export (Addresses Only)
```
1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q8R9S
1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T
...
```

### CSV Export (Addresses + Amounts)
```
address,amount
1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q8R9S,0.10000000
1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T,0.05000000
...
```

## Troubleshooting

### Common Issues

1. **"Please enter an extended public key" error**
   - Ensure the XPUB field is not empty
   - Check that your xpub starts with 'xpub' or 'tpub'

2. **"Minimum amount must be less than maximum amount" error**
   - In Random distribution mode, ensure min < max
   - Use the auto-suggested values or adjust manually

3. **GUI doesn't start**
   - Ensure PyQt6 is installed: `./venv/bin/pip install PyQt6`
   - Check that you're using the correct Python version
   - Try running: `make install` to reinstall dependencies

4. **Import errors**
   - Ensure you're in the correct directory
   - Check that the virtual environment is activated
   - Verify all files are present in the project structure

### Performance Notes

- Address generation runs in a background thread (UI remains responsive)
- Large address counts (>1000) may take some time
- Progress is indicated by the progress bar
- You can continue using other applications while generation runs

## Security Best Practices

1. **XPUB Handling**
   - Never share your extended private key (xprv)
   - Extended public keys (xpub) are safe to use but still sensitive
   - Clear the GUI input when done for privacy

2. **File Security**
   - Store generated files securely
   - Consider encrypting CSV files containing amounts
   - Use batch export for improved privacy

3. **Address Reuse**
   - The application tracks previous derivations
   - Always continue from last index to avoid address reuse
   - Don't manually restart from index 0 unless intended

## Integration with CLI

The GUI complements the existing CLI application:
- Same core functionality and algorithms
- Compatible file formats
- Shared state management
- Can switch between GUI and CLI workflows

Use `make run` for CLI or `make start-gui` for GUI. 