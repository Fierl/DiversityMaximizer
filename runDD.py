import cv2
import time
import math
import numpy
import json

from beamngpy import BeamNGpy, Scenario, Vehicle, setup_logging
from beamngpy.sensors import Camera, GForces, Electrics, Damage
from docutils.nodes import transition
from scenarioCreator import *

from shapely.geometry import Point

import speed_dreams as sd



BEAMNG_HOME="D:\\SimonFierbeck\\BeamNG.research_unlimited\\trunk"
pathToScenarioBeamng = 'd:/SimonFierbeck/BeamNG.research_unlimited/trunk/levels/asfault/scenarios'
pathToScenarioDocuments = 'c:/Users/Simon/Documents/BeamNG.research/levels/asfault/scenarios'

oobCount = 0
oobCountList = []
finalPath = 'd:/SimonFierbeck/AsFault/results/Set/'

def writeFile(oobList, segmentList, directoryCount):
    fileCount = 0
    with open(os.path.join(finalPath, str(directoryCount), 'oobCount' + '.txt'), 'w') as fp:
        for oob in oobList:
            fileCount = fileCount + 1
            fp.write("Count" + str(fileCount) + ": " + str(oob) + "\n")
        for segment in segmentList:
            fp.write(segment + " ")


def get_segment(test, state):
    network = test.network
    pos = Point(state['pos'][0], state['pos'][1])
    nodes = network.get_nodes_at(pos)
    if nodes:
        return nodes.pop()
    else:
        return None

def off_track(test, state):
    distance = get_centre_distance(test, state)
    if distance > 4 / 2.0:
        return True

    return False

def get_path_projection(test, state):
    path = test.get_path_polyline()
    point = Point(state['pos'][0], state['pos'][1])
    if point.geom_type != 'Point':
        l.error('Point is: %s', point.geom_type)
        raise ValueError('Not a point!')
    proj = path.project(point, normalized=True)
    proj = path.interpolate(proj, normalized=True)
    return proj


def get_centre_distance(test, state):
    proj = get_path_projection(test, state)
    pos = Point(state['pos'][0], state['pos'][1])
    distance = math.fabs(pos.distance(proj))

    network = test.network
    nodes = network.get_nodes_at(pos)
    if nodes:
        distance -= (4 + 0.2) / 2.0
    else:
        distance += (4 + 0.2) / 2.0

    distance = math.fabs(distance)
    return distance

def goal_reached(test, state):
    pos = Point(state['pos'][0], state['pos'][1])
    distance = pos.distance(test.goal)
    return distance < 10

def preprocess(img, brightness):

    # Elaborate Frame from BeamNG
    pil_image = img.convert('RGB')
    open_cv_image = numpy.array(pil_image)

    # Convert RGB to BGR. This is important
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    # decrease_brightness and resize
    hsv = cv2.cvtColor(cv2.resize(open_cv_image, (280, 210)), cv2.COLOR_BGR2HSV)
    hsv[..., 2] = hsv[..., 2] * brightness
    preprocessed = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # Check that we are passing to the network values between 0 and 1
    return preprocessed


def translate_steering(original_steering_value):
    # Using a quadratic function might be too much
    # newValue = -1.0 * (0.4 * pow(original_steering_value, 2) + 0.6 * original_steering_value + 0)
    # This seems to over shoot. Maybe it's just a matter of speed and not amount of steering
    newValue = -1.0 * original_steering_value
    linear_factor = 0.6
    # Dump the controller to compensate oscillations in gentle curve
    if abs(original_steering_value) < 1:
        newValue = linear_factor * newValue

    # print("Steering", original_steering_value, " -> ", newValue)
    return newValue


def main(MAX_SPEED):
    setup_logging()

    # Gains to port TORCS actuators to BeamNG
    # steering_gain = translate_steering()
    acc_gain = 0.5  # 0.4
    brake_gain = 1.0
    # BeamNG images are too bright for DeepDrive
    brightness = 0.4


    # Set up first vehicle
    # ! A vehicle with the name you specify here has to exist in the scenario
    vehicle = Vehicle('egovehicle')

    # Set up sensors

    # Set up sensors
    resolution = (280, 210)

    # Original Settings
    #pos = (-0.5, 1.8, 0.8)  # Left/Right, Front/Back, Above/Below
    # 0.4 is inside
    #pos = (-1.1, 1.4, 0.8)  # Left/Right, Front/Back, Above/Below
    pos = (-0.5, 1.8, 0.6)  # Left/Right, Front/Back, Above/Below
    # Are those what ? RAD ?

    # Rotate left or right. 0 Means center.
    A=0 # This one center the camera on the car position. negative offset left, positive offset right

    # This rotated
    B=1 # if 0 camera is upside down. if -1 is rear view. 1 Front view

    C=0 # pitch?
    # Is there any special convention?
    direction = (A, B, C)
    # direction = (180, 0, 180)

    # FOV 60, MAX_SPEED 100, 20 (3) Hz fails
    # FOV 60, MAX_jSPEED 80, 12 Hz Ok-ish Oscillations
    # FOV 60, MAX_SPEED 80, 10 Hz Ok-ish Oscillations
    # FOV 40, MAX_SPEED 50, 12 Hz Seems to be fine but drives slower
    # FOV 40, MAX_SPEED 80, 10 Hz Seems to be fine but drives slower

    fov =50
    # MAX_SPEED = 70
    MAX_FPS = 60
    # Increase the controller frequency to 20Hz
    SIMULATION_STEP = 6
    # Running the controller at 20 hz makes experiments 3 to 4 times slower ! 5 minutes of simulations end up sucking 20 minutes !
    #

    with open(pathToScenarioBeamng + '/asfault.json', 'r') as f:
        jsonScenario = json.load(f)
    with open(pathToScenarioBeamng + '/asfault.lua', 'r') as f:
        luaScenario = f.readlines()
    with open(pathToScenarioBeamng + '/asfault.prefab', 'r') as f:
        prefabScenario = f.readlines()
    with open(pathToScenarioDocuments + '/asfault.json', 'w') as outfile:
        json.dump(jsonScenario, outfile)
    with open(pathToScenarioDocuments + '/asfault.lua', 'w') as outfile:
        outfile.writelines(luaScenario)
    with open(pathToScenarioDocuments + '/asfault.prefab', 'w') as outfile:
        outfile.writelines(prefabScenario)

    # WORKING SETTINGS: 20 Freq, 90 FOV.
    # Near_far works like an ecografia quando e; abbastanza largo non fa
    # vedere l'interno della macchina ma manco la strada
    front_camera = Camera(pos, direction, fov, resolution, near_far=(0.5,300),
                          colour=True, depth=True, annotation=True)
    electrics = Electrics()

    vehicle.attach_sensor('front_cam', front_camera)
    vehicle.attach_sensor('electrics', electrics)

    # Setup the SHM with DeepDrive
    # Create shared memory object
    Memory = sd.CSharedMemory(TargetResolution=[280, 210])
    # Enable Pause-Mode
    Memory.setSyncMode(True)

    Memory.Data.Game.UniqueRaceID = int(time())
    print("Setting Race ID at ", Memory.Data.Game.UniqueRaceID)

    # Setting Max_Speed for the Vehicle.
    # TODO What's this? Maybe some hacky way to pass a parameter which is not supposed to be there...

    Memory.Data.Game.UniqueTrackID = int(MAX_SPEED)
    # Speed is KM/H
    print("Setting speed at ", Memory.Data.Game.UniqueTrackID)
    # Default for AsFault
    Memory.Data.Game.Lanes = 1
    # By default the AI is in charge
    Memory.Data.Control.IsControlling = 1

    deep_drive_engaged = True
    STATE = "NORMAL"

    Memory.waitOnRead()
    if Memory.Data.Control.Breaking == 3.0 or Memory.Data.Control.Breaking == 2.0:
        print("\n\n\nState not reset ! ", Memory.Data.Control.Breaking)
        Memory.Data.Control.Breaking = 0.0
        # Pass the computation to DeepDrive
        # Not sure this will have any effect
        Memory.indicateWrite()

    Memory.waitOnRead()
    if Memory.Data.Control.Breaking == 3.0 or Memory.Data.Control.Breaking == 2.0:
        print("\n\n\nState not reset Again! ", Memory.Data.Control.Breaking)
        Memory.Data.Control.Breaking = 0.0
        # Pass the computation to DeepDrive
        Memory.indicateWrite()
    global oobCount
    port = 50000
    count = 0
    while count < 72:
        testList = getTestsFromJson(os.path.join(finalPath, str(count)))
        segmentList = []
        for test in testList:
            createScenario(test)
            scenario = Scenario('asfault', 'asfault', True)
            # Connect to running beamng
            #global port
            print(port)
            beamng = BeamNGpy('localhost', port, home=BEAMNG_HOME)
            #bng = beamng.open(launch=False)
            bng = beamng.open(launch=True)
            scenario.make(bng)
            bng.load_scenario(scenario)
            sleep(3)
            bng.start_scenario()
            print('here')
            t_oob = time()
            t_end = time() + 60 * 3
            try:
                #bng.start_scenario()
                bng.set_deterministic()  # Set simulator to be deterministic
                bng.set_steps_per_second(120)  # With 60hz temporal resolution
                # Connect to the existing vehicle (identified by the ID set in the vehicle instance)
                bng.connect_vehicle(vehicle)
                # Put simulator in pause awaiting further inputs
                bng.pause()
                print('here #3')
                runningTest = True
                oobSegment = None
                assert vehicle.skt

                # Road interface is not available in BeamNG.research yet
                # Get the road map from the level
                # roads = bng.get_roads()
                # # find the actual road. Dividers lane markings are all represented as roads
                # theRoad = None
                # for road in enumerate(roads):
                #     # ((left, centre, right), (left, centre, right), ...)
                #     # Compute the width of the road
                #     left = Point(road[0][0])
                #     right = Point(road[0][1])
                #     distance = left.distance( right )
                #     if distance < 2.0:
                #         continue
                #     else:
                #         theRoad = road;
                #         break
                #
                # if theRoad is None:
                #     print("WARNING Cannot find the main road of the map")

                while runningTest:
                    # Resume the execution
                    # 6 steps correspond to 10 FPS with a resolution of 60FPS
                    # 5 steps 12 FPS
                    # 3 steps correspond to 20 FPS
                    bng.step(SIMULATION_STEP)

                    # Retrieve sensor data and show the camera data.
                    sensors = bng.poll_sensors(vehicle)
                    # print("vehicle.state", vehicle.state)

                    # # TODO: Is there a way to query for the speed directly ?
                    speed = math.sqrt(vehicle.state['vel'][0] * vehicle.state['vel'][0] + vehicle.state['vel'][1] * vehicle.state['vel'][1])
                    # Speed is M/S ?
                    # print("Speed from BeamNG is: ", speed, speed*3.6)

                    imageData = preprocess(sensors['front_cam']['colour'], brightness)

                    Height, Width = imageData.shape[:2]
                    # print("Image size ", Width, Height)
                    # TODO Size of image should be right since the beginning
                    Memory.write(Width, Height, imageData, speed)

                    # Pass the computation to DeepDrive
                    Memory.indicateWrite()

                    # Wait for the control commands to send to the vehicle
                    # This includes a sleep and will be unlocked by writing data to it
                    Memory.waitOnRead()

                    # TODO Assumption. As long as the car is out of the road for too long this value stays up
                    if Memory.Data.Control.Breaking == 3.0:
                        if STATE != "DISABLED":
                            print("Abnormal situation detected. Disengage DeepDrive and enable BeamNG AI")
                            vehicle.ai_set_mode("manual")
                            vehicle.ai_drive_in_lane(True)
                            vehicle.ai_set_speed(MAX_SPEED)
                            vehicle.ai_set_waypoint("waypoint_goal")
                            #oobCount = oobCount + 1
                            deep_drive_engaged = False
                            STATE = "DISABLED"
                    elif Memory.Data.Control.Breaking == 2.0:
                        if STATE != "GRACE":
                            print("Grace period. Deep Driving still disengaged")
                            vehicle.ai_set_mode("manual")
                            vehicle.ai_drive_in_lane(True)
                            vehicle.ai_set_speed(MAX_SPEED)
                            vehicle.ai_set_waypoint("waypoint_goal")
                            # vehicle.ai_drive_in_lane(True)
                            STATE = "GRACE"
                    else:
                        if STATE != "NORMAL":
                            print("DeepDrive re-enabled")
                            # Disable BeamNG AI driver
                            # vehicle.ai_set_mode("disabled")
                            deep_drive_engaged = True
                            STATE = "NORMAL"

                    # print("State ", STATE, "Memory ",Memory.Data.Control.Breaking )
                    if STATE == "NORMAL":
                        # vehicle.ai_set_mode("disabled")
                        # print("DeepDrive re-enabled")
                        # Disable BeamNG AI driver
                        vehicle.ai_set_mode("disabled")
                        # Get commands from SHM
                        # Apply Control - not sure cutting at 3 digit makes a difference
                        steering = round(translate_steering(Memory.Data.Control.Steering), 3)
                        throttle = round(Memory.Data.Control.Accelerating * acc_gain, 3)
                        brake = round(Memory.Data.Control.Breaking * brake_gain, 3)

                        # Apply commands
                        vehicle.control(throttle=throttle, steering=steering, brake=brake)
                        #
                        # print("Suggested Driving Actions: ")
                        # print(" Steer: ", steering)
                        # print(" Accel: ", throttle)
                        # print(" Brake: ", brake)
                    if off_track(test, vehicle.state):
                        print('off track')
                        segment = get_segment(test, vehicle.state)
                        if segment is not None and segment != oobSegment and t_oob < time():
                            currentSegmentDict = NetworkNode.to_dict(segment)
                            currentSegKey = currentSegmentDict['key']
                            segmentList.append(currentSegKey)
                        print(segmentList)
                        if segment == oobSegment or t_oob > time():
                            print('already counted')
                        else:
                            oobSegment = segment
                            t_oob = time() + 7
                            oobCount = oobCount + 1

                    if goal_reached(test, vehicle.state) or t_end < time():
                        global oobCountList
                        print('OobCount: ', oobCount)
                        if(t_end < time()):
                            oobCountList.append(1000)
                        else:
                            oobCountList.append(oobCount)
                        oobCount = 0
                        port = port + 10
                        runningTest = False

            finally:
                bng.close()
        writeFile(oobCountList, segmentList, count)
        segmentList = []
        oobCountList = []
        count = count + 1

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--max-speed', type=int, default=70, help='Speed Limit in KM/H')
    args = parser.parse_args()
    print("Setting max speed to", args.max_speed)
    main(args.max_speed)
