
# ### Code ###
from collections import namedtuple
import copy
import itertools
from more_itertools import peekable
from operator import itemgetter

from part import Part, BodyPart, JointPart, NeuronPart, SensorPart, WirePart
from blueprint_select import Body, Joint, Sensor, Wire


OutputBody = namedtuple('OutputBody', ['index', 'x_loc', 'y_loc',
                                       'z_loc', 'size'])
OutputJoint = namedtuple('OutputJoint', ['index', 'body1', 'body2',
                                         'x_loc', 'y_loc', 'z_loc',
                                         'x_axis', 'y_axis', 'z_axis',
                                         'lower_limit', 'upper_limit',
                                         'motor'])
OutputSensor = namedtuple('OutputSensor', ['sensor', 'body_index',
                                           'mount_x', 'mount_y',
                                           'mount_z'])


def frame_raiser(bodypart_list, jointpart_list):
    """Returns modified lists such that no part of the frame 
       initiates below the ground. (i.e., no y-value < .1)

    """
    for part in bodypart_list:
        points_below = []
        lowest_point = part.y_loc - part.size
        if lowest_point < .1:
            points_below.append((part.index, lowest_point))
    if points_below:
        lowest_point = min(points_below, key=itemgetter(1))[1]
        amount_to_raise = .1 - lowest_point
    
        for i in xrange(len(bodypart_list)):
            new_y = part.y_loc + amount_to_raise
            bodypart_list[i] = bodypart_list[i]._replace(y_loc=new_y)
        for i in xrange(len(jointpart_list)):
            new_y = part.y_loc + amount_to_raise
            bodypart_list[i] = bodypart_list[i]._replace(y_loc=new_y)
        return [bodypart_list, jointpart_list]
    else:
        return [bodypart_list, jointpart_list]


def setup_frame_to_send(parts_built, frame_parts):
    """Returns a list of frame_part lists to be exported to the 
       Bullet Physics code.

       Also exports the correctly rotated body_list.  It is important
       that this list gets used in the function
       setup_sensors_to_send().

    """
    body_list = [i for i in parts_built
                 if (i.__class__ == BodyPart and
                     i.characteristics.joint_mount_num > 0)]
    bodypart_list = []
    joint_list = [i for i in parts_built
                  if i.__class__ == JointPart]
    jointpart_list = []
    body_id = 0
    joint_id = 0

    making_base = body_list[0]
    size = making_base.characteristics.size
    x, y, z = 0., size, 0.
    out_body = OutputBody(body_id,
                          x, y, z,
                          size)
    bodypart_list.append(out_body)
    body_id += 1

    for part in frame_parts[1]:
        body_index = part.other_body
        making_body = body_list[body_index]
        size = making_body.characteristics.size
        base_index = part.base_body
        base = body_list[base_index]
        base_size = base.characteristics.size
        mount_vector = base.characteristics.joint_mount_loc[part.base_mount]

        joint_x = (bodypart_list[base_index].x_loc +
                   base_size * mount_vector[0])
        joint_y = (bodypart_list[base_index].y_loc +
                   base_size * mount_vector[1])
        joint_z = (bodypart_list[base_index].z_loc +
                   base_size * mount_vector[2])
        axis_decider = mount_vector.tolist().index(min(mount_vector))
        axis_x = 1 if axis_decider == 0 else 0
        axis_y = 1 if axis_decider == 1 else 0
        axis_z = 1 if axis_decider == 2 else 0

        making_joint = joint_list[part.joint]
        out_joint = OutputJoint(joint_id, base_index+1, body_id,
                                joint_x, joint_y, joint_z,
                                axis_x, axis_y, axis_z,
                                making_joint.characteristics.lower_limit,
                                making_joint.characteristics.upper_limit,
                                making_joint.characteristics.motor)
        jointpart_list.append(out_joint)
        joint_id += 1

        x = joint_x + size * mount_vector[0]
        y = joint_y + size * mount_vector[1]
        z = joint_z + size * mount_vector[2]
        making_body.rotate_body(mount_vector)
        rotated_body = making_body
        body_list[body_index] = rotated_body
        out_body = OutputBody(body_id,
                              x, y, z,
                              size)
        bodypart_list.append(out_body)
        body_id += 1
    bodypart_list, jointpart_list = frame_raiser(bodypart_list,
                                             jointpart_list)
    return [bodypart_list, jointpart_list, body_list]


def setup_sensors_to_send(sensor_parts, rotated_body_list):
    """Returns a list of sensor parts to be exported to the 
       Bullet Physics code.

       It is important that function uses the body_list returned 
       by the function setup_frame_to_send().

    """
    sensorpart_list = []
    for part in sensor_parts:
        body = rotated_body_list[part.body_index]
        mount_vector = body.characteristics.sensor_mount_loc[part.mount_used]
        x, y, z = mount_vector
        out_sensor = OutputSensor(part.sensor,
                                  part.body_index,
                                  x, y, z)
        sensorpart_list.append(out_sensor)
    return sensorpart_list


def find_wire_weight(wire_list, wire_parts, tos_type, tos, froms_type, froms):
    """Returns the sum of weights for the wires that matche input description.

       If wire isn't found, this returns 0. This is a helper function
       for make_matrix().

    """
    wire_index = [i.wire for i in wire_parts
                  if (i.from_type == froms_type and
                      i.from_index == froms and
                      i.to_type == tos_type and
                      i.to_index == tos)]
    return sum([wire_list[i].characteristics.weight
                for i in wire_index])


def make_matrix(wire_list, wire_parts, tos_type, tos, froms_type, froms):
    """Returns a input-->output matrix for the types specified in the inputs.

       This is a helper function for setup_ann_to_send().

    """
    matrix = []
    for i in xrange(froms):
        row = []
        for j in xrange(tos):
            row.append(find_wire_weight(wire_list, wire_parts, tos_type, j,
                                        froms_type, i))
        matrix.append(row)
    return matrix    


def setup_ann_to_send(parts_built, wire_parts, num_joints, 
                               num_neurons, num_sensors):
    """Returns matrices to be exported to Bullet Physics.
    
    """
    wire_list = [i for i in parts_built
                 if i.__class__ == WirePart]
    sensors_to_neurons = make_matrix(wire_list, wire_parts, NeuronPart,
                                     num_neurons, SensorPart, num_sensors)
    neurons_to_neurons = make_matrix(wire_list, wire_parts, NeuronPart,
                                     num_neurons, NeuronPart, num_neurons)
    sensors_to_joints = make_matrix(wire_list, wire_parts, JointPart,
                                     num_joints, SensorPart, num_sensors)
    neurons_to_joints = make_matrix(wire_list, wire_parts, JointPart,
                                     num_joints, NeuronPart, num_neurons)
    return [sensors_to_neurons, neurons_to_neurons,
            sensors_to_joints, neurons_to_joints]
