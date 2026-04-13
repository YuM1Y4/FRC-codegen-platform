package frc.robot;

import edu.wpi.first.wpilibj2.command.button.CommandXboxController;
import frc.robot.commands.AutoRoutines;
// __COMMAND_IMPORTS__
import frc.robot.constants.OperatorConstants;
// __SUBSYSTEM_IMPORTS__

public class RobotContainer {
  // __SUBSYSTEM_FIELDS__
  private final AutoRoutines autoRoutines = new AutoRoutines();
  private final CommandXboxController driverController =
      new CommandXboxController(OperatorConstants.DRIVER_CONTROLLER_PORT);

  public RobotContainer() {
    configureDefaultCommands();
    configureBindings();
    configureAutos();
  }

  private void configureDefaultCommands() {
    // __DEFAULT_COMMANDS__
  }

  private void configureBindings() {
    // __BINDINGS__
  }

  private void configureAutos() {
    autoRoutines.configure();
  }
}
