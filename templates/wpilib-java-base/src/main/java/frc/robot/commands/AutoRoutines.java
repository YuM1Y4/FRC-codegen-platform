package frc.robot.commands;

import java.util.function.Supplier;

import edu.wpi.first.wpilibj.smartdashboard.SendableChooser;
import edu.wpi.first.wpilibj.smartdashboard.SmartDashboard;
import edu.wpi.first.wpilibj2.command.Command;
import edu.wpi.first.wpilibj2.command.Commands;
import edu.wpi.first.wpilibj2.command.button.RobotModeTriggers;

public final class AutoRoutines {
  private final SendableChooser<Supplier<Command>> autoChooser = new SendableChooser<>();
  private Command activeAutoCommand = Commands.none();

  public void configure() {
    autoChooser.setDefaultOption("Do Nothing", Commands::none);
    SmartDashboard.putData("Auto Chooser", autoChooser);

    // Schedule the selected routine when autonomous starts and cancel it when the mode ends.
    RobotModeTriggers.autonomous().whileTrue(selectedCommandScheduler());
  }

  public void addRoutine(String name, Supplier<Command> commandFactory) {
    autoChooser.addOption(name, commandFactory);
  }

  private Command selectedCommandScheduler() {
    return Commands.startEnd(
        () -> {
          final Supplier<Command> selectedFactory = autoChooser.getSelected();
          activeAutoCommand = selectedFactory != null ? selectedFactory.get() : Commands.none();
          activeAutoCommand.schedule();
        },
        () -> {
          activeAutoCommand.cancel();
          activeAutoCommand = Commands.none();
        });
  }
}
