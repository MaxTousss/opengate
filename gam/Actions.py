import gam  # needed for gam_setup
import gam_g4 as g4


class Actions(g4.G4VUserActionInitialization):
    """
    TODO
    """

    def __init__(self, source):
        g4.G4VUserActionInitialization.__init__(self)
        self.g4_UserPrimaryGenerator = source
        self.g4_RunAction = None
        self.g4_EventAction = None
        self.g4_TrackingAction = None

    def __del__(self):
        pass

    def BuildForMaster(self):
        # function call only in MT mode
        print('Action::BuildForMaster')
        # set the actions for Run
        self.g4_RunAction = gam.RunAction()
        self.SetUserAction(self.g4_RunAction)
        print('should not be there for the moment (maybe later for multi thread)')
        exit(0)

    def Build(self):
        print("Action Build")
        # set the source first
        self.SetUserAction(self.g4_UserPrimaryGenerator)
        # set the actions for Run
        self.g4_RunAction = gam.RunAction()
        self.SetUserAction(self.g4_RunAction)
        # set the actions for Event
        self.g4_EventAction = gam.EventAction()
        self.SetUserAction(self.g4_EventAction)
        # set the actions for Track
        self.g4_TrackingAction = gam.TrackingAction()
        self.SetUserAction(self.g4_TrackingAction)
