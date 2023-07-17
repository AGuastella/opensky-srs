italian_bbox = 'lamin=36.619987291&lomin=6.7499552751&lamax=47.1153931748&lomax=18.4802470232'

# 34,4 50,22
bbox = 'lamin=34&lomin=4&lamax=50&lomax=22'


def is_in_italian_airspace(latitude, longitude):
    # Define the boundaries of the Italian airspace
    boundary_coordinates = [
        (38.611835, 7.140543),
        (34.808476, 15.055640),
        (39.938507, 19.540861),
        (45.084543, 13.288852),
        (45.452450, 14.575876),
        (47.548354, 12.572162),
        (45.707695, 6.108167)
    ]

    # Check if the point is within the boundaries
    in_airspace = False

    for i in range(len(boundary_coordinates)):
        j = (i + 1) % len(boundary_coordinates)
        if (boundary_coordinates[i][1] > longitude) != (boundary_coordinates[j][1] > longitude) and \
                latitude < (boundary_coordinates[j][0] - boundary_coordinates[i][0]) * (longitude - boundary_coordinates[i][1]) / \
                           (boundary_coordinates[j][1] - boundary_coordinates[i][1]) + boundary_coordinates[i][0]:
            in_airspace = not in_airspace

    return in_airspace