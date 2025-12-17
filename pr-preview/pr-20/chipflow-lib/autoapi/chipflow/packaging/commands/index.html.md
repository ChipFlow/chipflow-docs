# chipflow.packaging.commands

CLI commands for pin lock management.

## Classes

| [`PinCommand`](#chipflow.packaging.commands.PinCommand)   | CLI command handler for pin-related operations.   |
|-----------------------------------------------------------|---------------------------------------------------|

## Module Contents

### *class* chipflow.packaging.commands.PinCommand(config)

CLI command handler for pin-related operations.

This class provides the command-line interface for managing
pin allocations and lock files.

#### build_cli_parser(parser)

Build the CLI parser for pin commands.

Args:
: parser: argparse parser to add subcommands to

#### run_cli(args)

Execute the CLI command.

Args:
: args: Parsed command-line arguments

#### lock()

Lock the pin map for the design.

Will attempt to reuse previous pin positions.
