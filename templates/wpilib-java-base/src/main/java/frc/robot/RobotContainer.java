package frc.robot;

import edu.wpi.first.wpilibj2.command.Command;
import edu.wpi.first.wpilibj2.command.button.CommandXboxController;
import frc.robot.commands.Autos;
// __COMMAND_IMPORTS__
import frc.robot.constants.OperatorConstants;
// __SUBSYSTEM_IMPORTS__

public class RobotContainer {
  // __SUBSYSTEM_FIELDS__
  private final CommandXboxController driverController =
      new CommandXboxController(OperatorConstants.DRIVER_CONTROLLER_PORT);

  public RobotContainer() {
    configureDefaultCommands();
    configureBindings();
  }

  private void configureDefaultCommands() {
    // __DEFAULT_COMMANDS__
  }

  private void configureBindings() {
    // __BINDINGS__
  }

  public Command getAutonomousCommand() {
    return Autos.none();
  }
}
