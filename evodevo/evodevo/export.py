"""export --- a

"""
import os

from blueprint import OutputBody, OutputJoint, OutputSensor


def select_mode(blueprint_file):
    if os.path.isfile(blueprint_file):
        return 'w'
    else:
        return 'w+'


def export_bodys(body_blueprints):
    """Creates file that holds robot's bodypart info.

    """
    body_blueprints_file = '../io/body_blueprints_file.dat'
    mode = select_mode(body_blueprints_file)
    output_row = '{index},{x_loc},{y_loc},{z_loc},{size}\n'
    with open(body_blueprints_file, mode) as wf:
        for part in body_blueprints:
            wf.write(output_row.format(**part._asdict()))


def export_joints(joint_blueprints):
    """Creates file that holds robot's jointpart info.

    """
    joint_blueprints_file = '../io/joint_blueprints_file.dat'
    mode = select_mode(joint_blueprints_file)
    output_row = ('{index},{body1},{body2},{x_loc},{y_loc},'
                  '{z_loc},{x_axis},{y_axis},{z_axis},'
                  '{lower_limit},{upper_limit},{motor}\n')
    with open(joint_blueprints_file, mode) as wf:
        for part in joint_blueprints:
            wf.write(output_row.format(**part._asdict()))


def export_sensors(sensor_blueprints):
    """Creates file that holds robot's sensorpart info.

    """
    sensor_blueprints_file = '../io/sensor_blueprints_file.dat'
    mode = select_mode(sensor_blueprints_file)
    output_row = ('{sensor},{body_index},'
                  '{mount_x},{mount_y},{mount_z}\n')
    with open(sensor_blueprints_file, mode) as wf:
        for part in sensor_blueprints:
            wf.write(output_row.format(**part._asdict()))


def export_ann(s2n_blueprint, n2n_blueprint, s2j_blueprint,
               n2j_blueprint):
    """Creates file that holds robot's ANN info.

    """
    s2n_blueprint_file = '../io/s2n_blueprint_file.dat'
    n2n_blueprint_file = '../io/n2n_blueprint_file.dat'
    s2j_blueprint_file = '../io/s2j_blueprint_file.dat'
    n2j_blueprint_file = '../io/n2j_blueprint_file.dat'

    mode = select_mode(s2n_blueprint_file)
    with open(s2n_blueprint_file, mode) as wf:
        for row in s2n_blueprint:
            output_row = []
            for element in row:
                output_row.append(str(element))
            output_row = ','.join((output_row))
            output_row = ''.join((output_row, '\n'))
            wf.write(output_row)
    mode = select_mode(n2n_blueprint_file)
    with open(n2n_blueprint_file, mode) as wf:
        for row in n2n_blueprint:
            output_row = []
            for element in row:
                output_row.append(str(element))
            output_row = ','.join((output_row))
            output_row = ''.join((output_row, '\n'))
            wf.write(output_row)
    mode = select_mode(s2j_blueprint_file)
    with open(s2j_blueprint_file, mode) as wf:
        for row in s2j_blueprint:
            output_row = []
            for element in row:
                output_row.append(str(element))
            output_row = ','.join((output_row))
            output_row = ''.join((output_row, '\n'))
            wf.write(output_row)
    mode = select_mode(s2n_blueprint_file)
    with open(n2j_blueprint_file, mode) as wf:
        for row in n2j_blueprint:
            output_row = []
            for element in row:
                output_row.append(str(element))
            output_row = ','.join((output_row))
            output_row = ''.join((output_row, '\n'))
            wf.write(output_row)


def export_buffer():
    buffer_file = '../io/buffer.dat'
    with open(buffer_file, 'w+') as wf:
        wf.write("Hello World!")


def export_all(body_blueprints, joint_blueprints, sensor_blueprints,
               s2n_blueprint, n2n_blueprint, s2j_blueprint, n2j_blueprint):
    """Creates all files for robot's build info.

    """
    export_bodys(body_blueprints)
    export_joints(joint_blueprints)
    export_sensors(sensor_blueprints)
    export_ann(s2n_blueprint, n2n_blueprint, s2j_blueprint, n2j_blueprint)
    export_buffer()
