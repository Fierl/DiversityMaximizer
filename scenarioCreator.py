# this script is used to generate a scenario from an asfault generated road
# most of it is copy based from asfault
from OobSpeedSearch import *

PREFAB_FILE = 'asfault.prefab'
LUA_FILE = 'asfault.lua'
DESCRIPTION_FILE = 'asfault.json'
TEMPLATE_PATH = 'src/asfault/beamng_templates'

pathToScenarioBeamng = 'c:/Users/SimonFierbeck/seminar/research/levels/asfault/scenarios'
pathToScenarioDocuments = 'c:/Users/SimonFierbeck/Documents/BeamNG.research/levels/asfault/scenarios'

LANE_WIDTH = 4.0
WAYPOINT_STEP = 75.0

def write_scenario_prefab2(test_dir, test):
    # scenarios_dir = get_scenarios_dir(test_dir)
    prefab_file = os.path.join(test_dir, PREFAB_FILE)
    prefab = generate_test_prefab2(test)
    with open(prefab_file, 'w') as out:
        out.write(prefab)
    return prefab_file


def write_scenario_description2(test_dir, prefab):
    scenarios_dir = get_scenarios_dir(test_dir)
    if not os.path.exists(scenarios_dir):
        os.makedirs(scenarios_dir)
    description_file = os.path.join(scenarios_dir, DESCRIPTION_FILE)
    description = generate_test_description(prefab)
    with open(description_file, 'w') as out:
        out.write(description)
    return description_file



def prepare_waypoints2(test):
    path = test.get_path()
    if not path:
        return []

    ret = []
    path_poly = test.get_path_polyline()
    waypoint_count = math.ceil(path_poly.length / WAYPOINT_STEP)
    for idx in range(1, int(waypoint_count - 1)):
        offset = float(idx) / waypoint_count
        path_point = path_poly.interpolate(offset, normalized=True)
        box_cursor = box(path_point.x - 0.1, path_point.y - 0.1,
                         path_point.x + 0.1, path_point.y + 0.1)
        nodes = test.network.get_intersecting_nodes(box_cursor)

        if not nodes:
            continue

        if len(nodes) == 2 and test.network.is_intersecting_pair(*nodes):
            continue

        min_distance = sys.maxsize
        min_point = None
        min_node = None
        for node in nodes:
            if node not in path:
                continue
            spine = node.get_spine()
            if path_point.geom_type != 'Point':
                l.error('Point is: %s', path_point.geom_type)
                raise ValueError('Not a point!')
            spine_proj = spine.project(path_point, normalized=True)
            spine_proj = spine.interpolate(spine_proj, normalized=True)
            distance = path_point.distance(spine_proj)
            if distance < min_distance:
                min_distance = distance
                min_point = spine_proj
                min_node = node
        if not min_point:
            continue
        assert min_point

        l_lanes_c = len(min_node.l_lanes)
        r_lanes_c = len(min_node.r_lanes)

        scale = float(l_lanes_c + r_lanes_c) / 2
        scale = WAYPOINT_STEP * scale
        waypoint_id = '{}_{}'.format(min_node.seg_id, len(ret))
        waypoint = {'waypoint_id': waypoint_id, 'x': min_point.x,
                    'y': min_point.y,
                    'z': 0.01, 'scale': scale}
        ret.append(waypoint)

    nodes = test.network.get_nodes_at(test.goal)
    node = nodes.pop()
    l_lanes_c = len(node.l_lanes)
    r_lanes_c = len(node.r_lanes)
    scale = float(l_lanes_c + r_lanes_c) / 2
    goal_coords = {'waypoint_id': 'goal', 'x': test.goal.x, 'y': test.goal.y,
                   'z': 0.01, 'scale': WAYPOINT_STEP * scale}
    ret.append(goal_coords)

    return ret

def prepare_boundaries2(network):
    left, right = [], []
    roots = {*network.get_nodes(TYPE_ROOT)}
    while roots:
        root = roots.pop()
        left = get_street_boundary2(network, root, right=False)
        right = get_street_boundary2(network, root, right=True)
    return left, right

def get_street_boundary2(network, root, right=False):
    dividers = []

    coords = []
    last_cursor = None
    cursor = network.get_children(root)
    fmt = 'l{}'
    if right:
        fmt = 'r{}'
    while cursor:
        cursor = cursor.pop()
        if right:
            cursor_spine = cursor.get_right_edge()
            cursor_spine = cursor_spine.parallel_offset(
                LANE_WIDTH * 0.075, 'left', join_style=shapely.geometry.JOIN_STYLE.round)
        else:
            cursor_spine = cursor.get_left_edge()
            cursor_spine = cursor_spine.parallel_offset(
                LANE_WIDTH * 0.075, 'right', join_style=shapely.geometry.JOIN_STYLE.round)

        intersecting = network.get_segment_intersecting_nodes(cursor)
        if intersecting:
            intersection = intersecting.pop()
            before_coords, after_coords = get_intersection_dividers(
                cursor_spine, intersection)
            coords.extend(before_coords.coords)

            line = LineString(coords)
            divider = get_divider_from_polyline(
                root, fmt.format(len(dividers) + 1), line)
            dividers.append(divider)
            coords = [*after_coords.coords]
        else:
            if right:
                cursor_coords = cursor_spine.coords
                cursor_coords = cursor_coords[:-1]
            else:
                cursor_coords = cursor_spine.coords
                cursor_coords = list(reversed(cursor_coords[1:]))
            coords.extend(cursor_coords)

        last_cursor = cursor
        cursor = network.get_children(cursor)

    # Add the last segment's last coord, which is skipped usually to avoid
    # overlaps from segment to segment
    if right:
        cursor_spine = last_cursor.get_right_edge()
        cursor_spine = cursor_spine.parallel_offset(
            LANE_WIDTH * 0.075, 'left', join_style=shapely.geometry.JOIN_STYLE.round)
    else:
        cursor_spine = last_cursor.get_left_edge()
        cursor_spine = cursor_spine.parallel_offset(
            LANE_WIDTH * 0.075, 'right', join_style=shapely.geometry.JOIN_STYLE.round)
    cursor_coords = cursor_spine.coords
    if right:
        coords.append(cursor_coords[-1])
    else:
        coords.append(cursor_coords[0])
    line = LineString(coords)
    divider = get_divider_from_polyline(
        root, fmt.format(len(dividers) + 1), line)
    dividers.append(divider)

    return dividers

def generate_test_prefab2(test):
    streets = prepare_streets(test.network)
    dividers = prepare_dividers(test.network)
    l_boundaries, r_boundaries = prepare_boundaries2(test.network)
    path = test.path
    DIRECTION_AGNOSTIC_BOUNDARY = False
    if DIRECTION_AGNOSTIC_BOUNDARY and len(path) > 1:
        beg = path[0]
        nxt = path[1]
        if test.network.parentage.has_edge(nxt, beg):
            l_boundaries, r_boundaries = r_boundaries, l_boundaries
    waypoints = prepare_waypoints2(test)
    obstacles = prepare_obstacles(test.network)
    test_dict = {'start': {}, 'goal': {}}
    if 'start' in test_dict and test_dict['start']:
        test_dict['start'] = {'x': test.start.x, 'y': test.start.y, 'z': 0.01}
    else:
        test_dict['start'] = {'x': 0, 'y': 0, 'z': 0.01}

    if 'goal' in test_dict and test_dict['goal']:
        test_dict['goal'] = {'x': test.goal.x, 'y': test.goal.y, 'z': 0.01}
    else:
        test_dict['goal'] = {'x': 0, 'y': 0, 'z': 0.01}

    prefab = TEMPLATE_ENV.get_template(PREFAB_FILE).render(streets=streets,
                                                           dividers=dividers,
                                                           l_boundaries=l_boundaries,
                                                           r_boundaries=r_boundaries,
                                                           waypoints=waypoints,
                                                           obstacles=obstacles,
                                                           test=test_dict)
    return prefab

def getTestsFromJson(pathToDirectory):
    resList = []
    for file in os.listdir(pathToDirectory):
        if file.endswith(".json"):
            print(os.path.join(pathToDirectory, file))
            with open(os.path.join(pathToDirectory, file), 'r') as f:
                data = json.load(f)
                #print(data)
                test = RoadTest.from_dict(data)
                resList.append(test)
    return resList

def createScenario(test):
    ev = EvolutionConfig('c:/Users/SimonFierbeck/.asfaultenv/cfg/evolution.json')
    con = ev.get_default()
    prefabScenario = write_scenario_prefab2(pathToScenarioDocuments, test)
    jsonScenario = write_scenario_description2(pathToScenarioDocuments, prefabScenario)
    # with open(pathToScenarioDocuments + '/asfault.json', 'w') as outfile:
    #     json.dump(jsonScenario, outfile)
    # with open(pathToScenarioDocuments + '/asfault.prefab', 'w') as outfile:
    #     outfile.writelines(prefabScenario)

if __name__ == "__main__":
    c.get_defaults()
    testList = getTestsFromJson('c:/Users/SimonFierbeck/AsFault/results/Random/01')
    for test in testList:
        createScenario(test)

    vehicle = Vehicle('egovehicle')

    scenario = Scenario('asfault', 'asfault', True)

    beamng = BeamNGpy('localhost', 32513, home='c:/Users/SimonFierbeck/seminar/research')
    bng = beamng.open(launch=True)
    scenario.make(bng)
    bng.load_scenario(scenario)
    bng.start_scenario()
