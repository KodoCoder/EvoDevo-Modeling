
# ### Code ###
import os
import pprint as pp

import generate
import part
import prepare
import update
import blueprint_select
import blueprint_make
import blueprint_send


def check_it():
    global built_parts, osent_bodys, sent_joints, sent_sensors, sent_ann
    genomes = generate.generate(1, 18000)
    dev_parts = prepare.setup_agent(genomes[0])
    built_parts = update.update_cycles(dev_parts)
    frame_parts = blueprint_select.get_frame_parts(built_parts)
    neuron_parts, sensor_parts, wire_parts = blueprint_select.get_ann_parts(built_parts,
                                                                            frame_parts)
    pp.pprint([frame_parts[0], frame_parts[1],
               neuron_parts, sensor_parts, wire_parts])
    sent_bodys, sent_joints, rotated_bodys = blueprint_make.setup_frame_to_send(built_parts,
                                                                                frame_parts)
    sent_sensors = blueprint_make.setup_sensors_to_send(sensor_parts, 
                                                        rotated_bodys)
    sent_ann = blueprint_make.setup_ann_to_send(built_parts, wire_parts, 
                                                len(frame_parts[1]),
                                                len(neuron_parts),
                                                len(sensor_parts))
    wires = [i for i in built_parts if i.__class__ == part.WirePart]
    wire_weights = []
    for i in xrange(len(wire_parts)):
        wire_weights.append(wires[i].characteristics.weight)
    pp.pprint([sent_bodys, sent_joints, sent_sensors, sent_ann, wire_weights])
    blueprint_send.export_all(sent_bodys, sent_joints, sent_sensors,
                              *sent_ann)

    
