#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <exception>
#include <algorithm>
#include <math.h>
#include <time.h>
#include <cstdio>

using namespace std; 

#include "btBulletDynamicsCommon.h"
#include "GlutStuff.h"
#include "GL_ShapeDrawer.h"
#include "LinearMath/btIDebugDraw.h"
#include "GLDebugDrawer.h"
#include "BasicWorld.h"

#define COMMENTS false
#define RUNCOMMENTS false

//g++ -std=gnu++11 -g -v -I/root/sim/bullet-2.82-r2704/Demos/OpenGL/ -I/root/sim/bullet-2.82-r2704/src/ ./main.cpp -L/root/sim/bullet-build/Demos/OpenGl/ -L/root/sim/bullet-build/Demos/OpenGL/ -L/root/sim/bullet-build/src/BulletDynamics/ -L/root/sim/bullet-build/src/BulletCollision/ -L/root/sim/bullet-build/src/LinearMath -lOpenGLSupport -lGL -lGLU -lglut -lBulletDynamics -lBulletCollision -lLinearMath -o ./app

// Setup Collision Callback

static BasicWorld* basicWorld;

bool myContactProcessedCallback(btManifoldPoint& cp, void* body0, void* body1)
{
  int *ID1, *ID2;
  btCollisionObject* o1 = static_cast<btCollisionObject*>(body0);
  btCollisionObject* o2 = static_cast<btCollisionObject*>(body1);
  //int groundID = 0;
  
  ID1 = static_cast<int*>(o1->getUserPointer());
  ID2 = static_cast<int*>(o2->getUserPointer());
  if (RUNCOMMENTS)
    {cout << "ID1 = " << *ID1 << ", ID2 = " << *ID2 << endl;}
  
  basicWorld->touches[*ID1] = 1;
  basicWorld->touches[*ID2] = 1;
  basicWorld->touchPoints[*ID1] = cp.m_positionWorldOnB;
  basicWorld->touchPoints[*ID2] = cp.m_positionWorldOnB;

  return true;
}


// Initialize World

void BasicWorld::initPhysics()
{
  //collision stuff
  basicWorld = this;
  gContactProcessedCallback = myContactProcessedCallback;

  // ============= Getting, Manipulating, and Storing Blueprints ====================
  
  GrabBluePrints();

  // Set IDs and touches
  /*
  for (int i=0;i<body_indexs.size();i++)
    { 
      IDs.push_back(i);
      touches.push_back(0);
      touchPoints.push_back(btVector3(0.,0.,0.));
    }
  */
  /* was thinking about setting it per sensor
     but that doesn't make sense b/c the callback method 
     points to bodies
     Now trying to do it right before bodies get built
  */
  // But still need to set ground ID
  IDs.clear();
  IDs.reserve(body_indexs.size());
  IDs.push_back(0);
  touches.clear();
  touches.push_back(0);
  touchPoints.clear();
  touchPoints.push_back(btVector3(0.,0.,0.));
  
  timeStep = 0;
  pause = false;
  oneStep = false;


  if (body_indexs.empty()||joint_indexs.empty())
    {
      if (COMMENTS)
	{cout << "No bodies or No joints" << endl;}
      Save_Position(false);
      exit(0);
    }
      
  
  // Print out imported info
  if (COMMENTS)
    {
      PrintTestI(body_indexs);
      PrintTestS(body_kinds);
      PrintTestD(body_sizes);
      PrintTestI(body_j_nums);
      PrintTest2(body_j_locs);
      PrintTestI(body_n_nums);
      PrintTestI(body_s_nums);
      PrintTest2(body_s_locs);
      cout << endl;
      
      PrintTestI(joint_indexs);
      PrintTestB(joint_motors);
      PrintTestB(joint_frees);
      PrintTestD(joint_u_limits);
      PrintTestD(joint_l_limits);
      PrintTestI(joint_inputs);
      cout << endl;

      PrintTestI(neuron_indexs);
      PrintTestI(neuron_inputs);
      PrintTestI(neuron_outputs);
      cout << endl;
      
      PrintTestI(sensor_indexs);
      PrintTestI(sensor_outputs);
      cout << endl;
      
      PrintTestI(wire_indexs);
      PrintTestD(wire_weights);
      PrintTestB(wire_directs);
      cout << endl;
    }
  // ============== Basic World Setup =================
  //Texture, Cameras, and Shadows
  setTexturing(true);
  setShadows(true);
  
  setCameraDistance(btScalar(30.));
  
  //Setup and build Broadphase
  btVector3 worldAabbMin(-10000,-10000,-10000);
  btVector3 worldAabbMax(10000,10000,10000);
  //btBroadphaseInterface* define is in .h file 
  m_broadphase = new btAxisSweep3 (worldAabbMin, worldAabbMax);

  //Setup collision configuration and dispatcher
  //btDefaultCollisionConfiguration* define is in .h file 
  m_collisionConfiguration = new btDefaultCollisionConfiguration();
  //btCollisionDispatcher* define is in .h file 
  m_dispatcher = new btCollisionDispatcher(m_collisionConfiguration);

  // Physics solver
  //btConstraintSolver* define is in .h file 
  m_solver = new btSequentialImpulseConstraintSolver;

  // The world
  //btDiscreteDynamicsWorld* define is in .h file 
  m_dynamicsWorld = new btDiscreteDynamicsWorld(m_dispatcher, m_broadphase, m_solver, m_collisionConfiguration);
  // Don't forget the gravity!
  m_dynamicsWorld->setGravity(btVector3(0, -9.81, 0));

  // ================ Objects  ========================

  // Ground and sphere collision shape variables
  //btCollisionShape* define is in .h file 

  groundShape = new btStaticPlaneShape(btVector3(0, 1, 0), 1);
  m_collisionShapes.push_back(groundShape);

  btTransform groundTransform;
  groundTransform.setIdentity();
  groundTransform.setOrigin(btVector3(0,-1,0));

  fixedGround = new btCollisionObject();
  fixedGround->setCollisionShape(groundShape);
  fixedGround->setWorldTransform(groundTransform);
  fixedGround->setUserPointer(&(IDs[0]));
  m_dynamicsWorld->addCollisionObject(fixedGround);  
  
  //=================== Creating Body Parts and Joints ================================
  
  // these hold all create information
  vector<vector<btScalar> > parts_to_build;
  vector<vector<btScalar> > hinges_to_build; 
  parts_to_build.clear();
  hinges_to_build.clear();
  vector<btScalar> tb_holder;
  vector<btVector3> bp_locations;
  // the following three use same indexing as BP bodies
  vector<int> body_built(body_indexs.size(), 0);
  vector<int> tossed_bodys(body_indexs.size(), 0);
  vector<int> used_joints(body_indexs.size(), 0);
  // Note, "used_joints" can be used as an index for the current joint to use: e.g.
  // if one joint has been used, the second joint (indexed as 1) will be called.
  // Indexed like bp_attributes
  // index of current part in bp_attribute lists
  int index = 0;
  // index of BP joints
  int j_index = 0;
  // index of BP bodies
  // b_index[n] is the b_number for bodypart associated with index n
  vector<int> b_index(body_indexs.size(), 0);
  // vars for locs of bp, joint, and joint-axis.
  btScalar x = 0.;
  btScalar y = 0.;
  btScalar z = 0.;
  btScalar j_x;
  btScalar j_y;
  btScalar j_z;
  btScalar a_x = 1.;
  btScalar a_y = 0.;
  btScalar a_z = 0.;
  double size_now = 0;
  // index of bp_attributes for base of next part
  int base_index = 0;
  // accumilator of BPs tossed
  int t_acc = 0;
  // accumilator of BPs used
  int b_acc = 0;
  
  do
    {   
      if (COMMENTS)
	{
	  cout << endl;
	  cout << "Index: " << index << "| B_Index: " << b_index[index] << "| Joints total: " << body_j_nums[index] << "| Joints used: " << used_joints[index] << endl;
	  cout << "Base Index: " << base_index << "| B_Index: " << b_index[base_index] << "| Joints total: " << body_j_nums[base_index] << "| Joints used: " << used_joints[base_index] << endl;
	} 
      // First part gets built at origin
      if (bp_locations.empty())
	{
	  if (body_j_nums[index] > 0)
	    {
	      //CreateSphere(b_index[b_acc], x, y, z, body_sizes[index]);
	      tb_holder.push_back(b_index[b_acc]);
	      tb_holder.push_back(x);
	      tb_holder.push_back(y);
	      tb_holder.push_back(z);
	      tb_holder.push_back(body_sizes[index]);
	      parts_to_build.push_back(tb_holder);
	      tb_holder.clear();
	      body_built[index] = 1;
	      built_bodies.push_back(index);
	      bp_locations.push_back(btVector3(x,y,z));
	      base_index = index;
	      index++;
	      b_acc++;
	      if (COMMENTS)
		{
	      cout << "Made object " << (index-1) << endl;
	      cout << "b_index: " << b_index[index-1] << endl;
		}
	    }
	  else 
	    {
	      //No Joint mounts, toss it
	      tossed_bodys[index] = 1;
	      t_acc++;
	      index++;
	      //if no part has joints, bail
	      if (index >= body_indexs.size())
		{
		  if (COMMENTS)
		    {
		  cout << "Bailed at start" << endl;
		    }
		  break;
		}
	      if (COMMENTS)
		{
		  cout << "Skipped object " << index-1 << " at 1" << endl;
		  cout << "J_num = " << body_j_nums[index-1] << endl;
		}
	      continue;
	    }
	}
      
      // index out of range? Start at begining!
      else if (index >= body_indexs.size())
	{ index = 0;
	  if (COMMENTS)
	    {
	      cout << "Out of range. Reset." << endl;
	    }
	}

      // Index is the same as base? Get next index!
      else if (index==base_index)
	{ index++;
	  if (COMMENTS)
	    {
	      cout << "Index and base equal..." << endl;
	    }
	}
     
      //maybe not needed because of last conditions
      // Built or tossed index? Go to the next one!
      else if (body_built[index]==1 || tossed_bodys[index]==1)
	{ index++;
	  if (COMMENTS)
	    {
	      cout << "Already used or tossed body " << index-1 << endl;
	    }
	}
      // No Joint Mounts? Toss it! 
      else if (body_j_nums[index]==0)
	{
	  tossed_bodys[index] = 1;
	  t_acc++;
	  index ++;
	  if (COMMENTS)
	    {
	      cout << "Skipped object " << (index-1) << " at 2" << endl;
	      cout << "J_num = " << body_j_nums[index-1] << endl;
	    }
	}
      // All other parts while they have a joint loc and base has free joint loc
      else if ((used_joints[index] < body_j_nums[index]) && (used_joints[base_index] <body_j_nums[base_index]))
	{
	  /*
	  while ((used_joints[index] < body_j_nums[index]) && (used_joints[base_index] < body_j_nums[base_index]) && index < body_indexs.size())
	    
	  {
	  */
	  // Set position vars of joint
	  if (COMMENTS)
	    {
	      cout << "Base Position: " << bp_locations[b_index[base_index]].x() << ',' << bp_locations[b_index[base_index]].y() << ',' << bp_locations[b_index[base_index]].z() << endl;
	      cout << "Base Size: " << body_sizes[base_index] << endl;
	    }
	  size_now = body_sizes[base_index];
	  j_x = bp_locations[b_index[base_index]].x() + (size_now * body_j_locs[base_index][used_joints[base_index]][0]);
	  j_y = bp_locations[b_index[base_index]].y() + (size_now * body_j_locs[base_index][used_joints[base_index]][1]);
	  j_z = bp_locations[b_index[base_index]].z() + (size_now * body_j_locs[base_index][used_joints[base_index]][2]);
	  if (COMMENTS)
	    {cout << "New Joint Position " << j_x << ',' << j_y << ',' << j_z << endl;}
	  // Set position vars of part
	  x = j_x - (size_now * body_j_locs[index][used_joints[index]][0]);
	  y = j_y - (size_now * body_j_locs[index][used_joints[index]][1]);
	  z = j_z - (size_now * body_j_locs[index][used_joints[index]][2]);
	  if (COMMENTS)
	    {
	      cout << "New Part Size: " << body_sizes[index] << endl;
	      cout << "New Part Position: " << x << ',' << y << ',' << z << endl;
	    }
	  //Create next part
	  //but first set b_index for new part
	  b_index[index] = b_acc;
	  built_bodies.push_back(index);
	  //CreateSphere(b_index[index], x, y, z, body_sizes[index]);
	  tb_holder.push_back(b_index[index]);
	  tb_holder.push_back(x);
	  tb_holder.push_back(y);
	  tb_holder.push_back(z);
	  tb_holder.push_back(size_now);
	  parts_to_build.push_back(tb_holder);
	  tb_holder.clear();
	  body_built[index] = 1;
	  bp_locations.push_back(btVector3(x,y,z));
	  if (COMMENTS)
	    {
	      cout << "Made object " << index << endl;
	      cout << "b_index: " << b_index[index] << endl;
	    }
	  //Create hinge between the two
	  //but first set  axis vars
	  //or maybe not
	  
	  // CreateHinge(j_index, b_index[base_index], b_index[index], btVector3(j_x,j_y,j_z), btVector3(a_x,a_y,a_z), joint_l_limits[j_index], joint_u_limits[j_index], joint_motors[j_index]);
	  tb_holder.push_back(j_index);
	  tb_holder.push_back(b_index[base_index]);
	  tb_holder.push_back(b_index[index]);
	  tb_holder.push_back(j_x);
	  tb_holder.push_back(j_y);
	  tb_holder.push_back(j_z);
	  tb_holder.push_back(a_x);
	  tb_holder.push_back(a_y);
	  tb_holder.push_back(a_z);
	  tb_holder.push_back(joint_l_limits[j_index]);
	  tb_holder.push_back(joint_u_limits[j_index]);
	  tb_holder.push_back(joint_motors[j_index]);
	  hinges_to_build.push_back(tb_holder);
	  tb_holder.clear();
	  built_joints.push_back(j_index);
	  used_joints[index]++;
	  used_joints[base_index]++;
	  if (COMMENTS)
	    {
	      cout << "Made hinge between " << base_index << " and " << index << " using joint " << j_index << endl;
	      cout << "b_index: " << b_index[index] << " base_b_index: " << b_index[base_index] << endl;
	    }
	  
	  //Recalculate indexes 
	  j_index ++;
	  if (j_index >= joint_indexs.size())
	    { if (COMMENTS)
		{cout << "Ran out of joints!" << endl;}
	      t_acc = body_indexs.size();
	      break;}
	  base_index = index; 	  
	  index++;
	  b_acc++;
	  //can't set next b_index now, because it's unclear if the next index used will be the next index just iterated to.
	}
      
      
      // if index doesn't have joint locs, try from start next
      else if (used_joints[index] >= body_j_nums[index])
	{
	  index=0;
	  //if it has been built/tossed, or if it has run out of joint locs, pick the next one instead
	  while (body_built[index]==1 || tossed_bodys[index]==1 || used_joints[index]>=body_j_nums[index])
	    {
	      index++;
	      // if we reach the end of the list, we're out of parts to build
	      if (index >= body_indexs.size())
		{ if (COMMENTS)
		    {cout << "Reached the last usuable part" << endl;}
		  t_acc = body_indexs.size();
		  break;}
	    }
	  if (COMMENTS)
	    {cout << "Try new index " << index << endl;}
	}
      
      // else: base_index doesn't have joint locs, so try next
      else if (used_joints[base_index] >= body_j_nums[base_index])
	{
	  base_index++;
	  bool looped = false;
	  //(if it hasn't been built or while it has been tossed) or if it has run out of joints locs, check the next one
	  while (body_built[base_index]==0 || tossed_bodys[base_index]==1 || used_joints[base_index]>=body_j_nums[base_index])
	    {
	      base_index++;
	      if (base_index >= body_indexs.size() && looped)
		{ if (COMMENTS)
		    {cout << "Reached the last usable base" << endl;}
		  t_acc = body_indexs.size();
		  break;}
	      if (base_index >= body_indexs.size())
		{base_index=0;
		  looped = true;}
	    }
	  if (COMMENTS)
	    {cout << "Try next base_index " << base_index << endl;}
	}
      
      else 
	{
	  if (COMMENTS)
	    {cout << "Got to end: " << used_joints[base_index] << '|' << body_j_nums[base_index] << endl;}
	}
    } while (bp_locations.size() < (body_indexs.size()-t_acc));

  
  //======================= Build The Body ===============================
  
  // Holds the maximum offset need to make the body start above the ground.

  btScalar vert_offset = 0;
  //bool use_offset = false;

  if (built_bodies.empty()||hinges_to_build.empty())
    {
      if (COMMENTS)
	{ cout << "No bodies or no joints to build" << endl;}
      Save_Position(false);
      exit(0);
    }
  
  for (int i=0;i<built_bodies.size();i++)
    { 
      IDs.push_back(i+1);
      touches.push_back(0);
      touchPoints.push_back(btVector3(0.,0.,0.));
    }
		       

  for (int i=0; i<parts_to_build.size(); i++)
    {
      vert_offset = min(parts_to_build[i][2] - parts_to_build[i][4], vert_offset);
    }

  if (COMMENTS)
    {cout << "Offset needed: " << vert_offset << endl;}

  if (vert_offset < 0)
    {
      vert_offset = -1*vert_offset + .1;
      if (COMMENTS)
	{cout << "Offset used: " << vert_offset << endl;}
      for (int i=0; i<parts_to_build.size(); i++)
	{
	  parts_to_build[i][2] = parts_to_build[i][2] + vert_offset;
	}
      for (int i=0; i<hinges_to_build.size(); i++)
	{
	  hinges_to_build[i][4] = hinges_to_build[i][4] + vert_offset;
	}
    }
    
  if (COMMENTS)
    {cout << "Done with body setup, start bulding" << endl;}

  for (int i=0; i<parts_to_build.size(); i++)
    {
      if (i==0)
	{
	  CreateSphere(parts_to_build[i][0], parts_to_build[i][1], parts_to_build[i][2], parts_to_build[i][3], parts_to_build[i][4]);
	}
      else
	{
	  int i_h = i-1; 
	  CreateSphere(parts_to_build[i][0], parts_to_build[i][1], parts_to_build[i][2], parts_to_build[i][3], parts_to_build[i][4]);
	  CreateHinge(hinges_to_build[i_h][0], hinges_to_build[i_h][1], hinges_to_build[i_h][2], hinges_to_build[i_h][3], hinges_to_build[i_h][4], hinges_to_build[i_h][5], hinges_to_build[i_h][6], hinges_to_build[i_h][7], hinges_to_build[i_h][8], hinges_to_build[i_h][9], hinges_to_build[i_h][10], hinges_to_build[i_h][11]);
	}
    }
  
  //body_touches holds the touch_index for the built bodys
  body_touches.clear();
  body_touches.reserve(body_built.size());
  int touch_count = 1;
  for (int i=0; i < body_built.size(); i++)
    {
      if (body_built[i]==1)
	{
	  body_touches.push_back(touch_count);
	  touch_count++;
	}
      else
	{
	  body_touches.push_back(0);
	}
    }
  
  if (COMMENTS)
    {
      cout << "Built:" << endl;
      for (int i=0; i<built_bodies.size(); i++)
	{
	  cout << "Part " << built_bodies[i] << endl;
	}
      for (int i=0; i<body_touches.size(); i++)
	{
	  cout << "Touch " << body_touches[i] << endl;
	}
    }

  if (COMMENTS)
    {cout << "Done with body building, start sensor and neurons" << endl;}

  //=============== Build Sensors and Neurons===========================================
  vector<int> used_s_mounts(body_indexs.size(), 0);
  vector<int> used_n_mounts(body_indexs.size(), 0);
  
  vector<int> v_holder;

  int s_index = 0;
  int n_index = 0;
  
  int sensor_capacity = 0;
  int neuron_capacity = 0;
  //Calculate total sensor and neuron mount slots
  for (int i=0; i<body_indexs.size(); i++)
    {
      if (body_built[i]==1)
	{
	  sensor_capacity += body_s_nums[i];
	  neuron_capacity += body_n_nums[i];
	}
    }    

  int sensor_total = sensor_indexs.size();
  int neuron_total = neuron_indexs.size();

  // While all sensors aren't built and all slots aren't taken up
  while ((built_sensors.size() < sensor_total) && (built_sensors.size() < sensor_capacity))
  // For all potential parts
    {
      for (int i=0; i<body_indexs.size(); i++)
	{
	  // Add sensors to built parts
	  if (body_built[i]==1)
	    {
	      // if part has free mounts for it
	      if ((body_s_nums[i] - used_s_mounts[i]) > 0)
		{
		  v_holder.push_back(s_index);
		  v_holder.push_back(i);
		  v_holder.push_back(used_s_mounts[i]);
		  built_sensors.push_back(v_holder);
		  if ((built_sensors.size()==sensor_total) || (built_sensors.size()==sensor_capacity))
		    { v_holder.clear();
		      break;}
		  v_holder.clear();
		  s_index++;
		}
	    }
	}    
    }

  // set sensor_touches now
  sensor_touches.clear();
  sensor_touches.resize(built_sensors.size());
  sensor_touches.reserve(built_sensors.size());
  
  /* Nope
  for (int i=0;i<built_sensors.size();i++)
    { 
      IDs.push_back(i);
      touches.push_back(0);
      touchPoints.push_back(btVector3(0.,0.,0.));
    }
  */

  while ((built_neurons.size() < neuron_total) && (built_neurons.size() < neuron_capacity))
    {
      for (int i=0; i<body_indexs.size(); i++)
	{
	  if (body_built[i]==1)
	    {
	      if ((body_n_nums[i] - used_n_mounts[i]) > 0)
		{
		  v_holder.push_back(n_index);
		  v_holder.push_back(i);
		  built_neurons.push_back(v_holder);
		  if ((built_neurons.size()==neuron_total) || (built_neurons.size()==neuron_capacity))
		    { v_holder.clear();
		      break;}
		  v_holder.clear();
		  n_index++;
		}
	    }
	}
    }     

  if (COMMENTS)
    {
      cout << endl << built_sensors.size() << " Sensors!" << endl << endl;
      
      for (int i=0; i<built_sensors.size(); i++)
	{
	  cout << built_sensors[i][0] << ',' << built_sensors[i][1] << endl;
	}
      
      cout << endl << built_neurons.size() << " Neurons!" << endl << endl;
      
      for (int i=0; i<built_neurons.size(); i++)
	{
	  cout << built_neurons[i][0] << ',' << built_neurons[i][1] << endl;
	}
    }

	
	 
  //====================== Build Wires ===========================================

  // use same index that "built_" lists do
  vector<int> used_s_outputs(built_sensors.size(), 0);
  vector<int> used_n_inputs(built_neurons.size(), 0);
  vector<int> used_n_outputs(built_neurons.size(), 0);
  vector<int> used_j_inputs(built_joints.size(), 0);

  // uses same index that "built_" lists do
  vector<int> tossed_sensors(built_sensors.size(), 0);
  vector<int> tossed_neurons(built_neurons.size(), 0);
  
  int wire_total = wire_indexs.size();
  int output_total = 0;
  int output_s_total = 0;
  int output_n_total = 0;
  for (int i=0; i<built_sensors.size(); i++)
    {
      output_s_total += sensor_outputs[built_sensors[i][0]];
    }
  for (int i=0; i<built_neurons.size(); i++)
    {
      output_n_total += neuron_outputs[built_neurons[i][0]];
    }

  output_total = output_s_total + output_n_total;

  int input_total = 0;
  int input_j_total = 0;
  int input_n_total = 0;
  for (int i=0; i<built_joints.size(); i++)
    {
      input_j_total += joint_inputs[built_joints[i]];
    }
  for (int i=0; i<built_neurons.size(); i++)
    {
      input_n_total += neuron_inputs[built_neurons[i][0]];
    }
  input_total = input_j_total + input_n_total;
  
  j_index = 0;
  s_index = 0; 
  n_index = 0;
  int s_global = 0;
  int n_global = 0;
  int w_index = 0;
  // false means from_neuron
  bool from_sensor = true;
  // false means to_neuron
  bool to_joint = wire_directs[0];
  bool found_joint = true;
  bool found_neuron = true;
  v_holder.clear();
  
  /*
  if (COMMENTS)
    {
      cout << endl;
      cout << "Wires Total: " << wire_total << endl;
      cout << "Joint Inputs: " << input_j_total << endl;
      cout << "Used Joint Inputs: " << used_part_counter(used_j_inputs) << endl; 
      cout << "Neuron Inputs: " << input_n_total << endl;
      cout << "Used Neuron Inputs: " << used_part_counter(used_n_inputs) << endl;
      cout << "Sensor Ouputs: " << output_s_total << endl;
      cout << "Used Sensor Outputs: " << used_part_counter(used_s_outputs) << endl;
      cout << "Neuron Ouputs: " << output_n_total << endl;
      cout << "Used Neuron Outputs: " << used_part_counter(used_n_outputs) << endl;  
    }
  */
  // Build Wires
  // While unused wire parts, and some combo of open outputs and inputs
  while ((wire_total > (built_s_wires.size()+built_n_wires.size()))&&
	 ((input_total > (used_part_counter(used_n_inputs) + used_part_counter(used_j_inputs)))&&
	  (output_total > (used_part_counter(used_s_outputs) + used_part_counter(used_n_outputs))))&&
	 (w_index < wire_total))
    {
      if (COMMENTS)
	{
	  cout << endl;
	}
      // sensor iteraton
      if (from_sensor)
	{
	  // for each sensor
	  for (int i=0; i < built_sensors.size(); i++)
	    {
	      // global index of built sensor
	      s_global = built_sensors[i][0];
	      // if it has free outputs, build a wire from it
	      if (sensor_outputs[s_global] > used_s_outputs[i])
		{
		  // if to_joint
		  if (to_joint)
		    {
		      i_hold = j_index;
		      // if not an empty slot in this joint
		      while (!(joint_inputs[built_joints[j_index]] > used_j_inputs[j_index]))
			{
			  // look in others
			  j_index++;
			  // keep looking
			  if (j_index >= built_joints.size())
			    {j_index = 0;}
			  // until you go through once
			  if (j_index == i_hold)
			    { found_joint = false;
			      break;}
			}
		      // If you find a good joint
		      if (found_joint)
			{
			  // set up wire
			  v_holder.push_back(w_index);
			  v_holder.push_back(s_global);
			  v_holder.push_back(built_joints[j_index]);
			  v_holder.push_back(0);
			  // build it
			  built_s_wires.push_back(v_holder);
			  if (COMMENTS)
			    {cout << "Built Wire--SJa: " << v_holder[0] << endl;}
			  used_j_inputs[j_index]++;
			  j_index++;
			  if (j_index >= built_joints.size())
			    {j_index = 0;}
			}
		     
		      // If you don't find a good joint
		      else  
			{
			  i_hold = n_index;
			  // look for a good neuron
			  while (!(neuron_inputs[built_neurons[n_index][0]] > used_n_inputs[n_index]))
			    {
			      n_index++;
			      if (n_index >= built_neurons.size())
				{n_index = 0;}
			      if (n_index==i_hold)
				{ found_neuron = false;
				  break;}
			    }
			  // If you find a good neuron
			  if (found_neuron)
			    {
			      // set up wire
			      v_holder.push_back(w_index);
			      v_holder.push_back(s_global);
			      v_holder.push_back(built_neurons[n_index][0]);
			      v_holder.push_back(1);
			      // build it
			      built_s_wires.push_back(v_holder);
			      if (COMMENTS)
				{cout << "Built Wire--SNb: " << v_holder[0] << endl;}
			      used_n_inputs[n_index]++;
			      n_index++;
			      if (n_index >= built_neurons.size())
				{n_index=0;}
			    }
			}
		      // and get ready for next step
		      if (found_joint||found_neuron)
			{
			  if (COMMENTS)
			    {cout << "test--SJ" << endl;}
			  v_holder.clear();
			  used_s_outputs[i]++;
			  w_index++;
			  if (w_index >= wire_total)
			    {break;}
			  to_joint = wire_directs[w_index];
			}
		      else 
			{
			  found_joint = true;
			  found_neuron = true;
			  if (COMMENTS)
			    {cout << "Nothing on this run vSJ" << endl;}
			}
		    }
		  // Or you look for a neuron first
		  else
		    {
		      i_hold = n_index;
		      // look for a good neuron
		      while (!(neuron_inputs[built_neurons[n_index][0]] > used_n_inputs[n_index]))
			{
			  n_index++;
			  if (n_index >= built_neurons.size())
			    {n_index = 0;}
			  if (n_index==i_hold)
			    { found_neuron = false;
			      break;}
			}
		      // If you find a good neuron
		      if (found_neuron)
			{
			  // set up wire
			  v_holder.push_back(w_index);
			  v_holder.push_back(s_global);
			  v_holder.push_back(built_neurons[n_index][0]);
			  v_holder.push_back(1);
			  // build it
			  built_s_wires.push_back(v_holder);
			  if (COMMENTS)
			    {cout << "Built Wire--SNa: " << v_holder[0] << endl;}
			  used_n_inputs[n_index]++;
			  n_index++;
			  if (n_index >= built_neurons.size())
			    {n_index=0;}
			}
		      // If you don't find a good neuron
		      else 
			{
			  // look for a joint instead
			  i_hold = j_index;
			  // if not an empty slot in this joint
			  while (!(joint_inputs[built_joints[j_index]] > used_j_inputs[j_index]))
			    {
			      // look in others
			      j_index++;
			      // keep looking
			      if (j_index >= built_joints.size())
				{j_index = 0;}
			      // until you go through once
			      if (j_index == i_hold)
				{ found_joint = false;
				  break;}
			    }
			  // If you find a good joint
			  if (found_joint)
			    {
			      // set up wire
			      v_holder.push_back(w_index);
			      v_holder.push_back(s_global);
			      v_holder.push_back(built_joints[j_index]);
			      v_holder.push_back(0);
			      // build it
			      built_s_wires.push_back(v_holder);
			      if (COMMENTS)
				{cout << "Built Wire--SJb: " << v_holder[0] << endl;}
			      used_j_inputs[j_index]++;
			      j_index++;
			      if (j_index >= built_joints.size())
				{j_index = 0;}
			    }
			}
		      
		      // and get ready for next step
		      if (found_joint||found_neuron)
			{
			  if (COMMENTS)
			    {cout << "test--SN" << endl;}
			  v_holder.clear();
			  used_s_outputs[i]++;
			  w_index++;
			  if (w_index >= wire_total)
			    {break;}
			  to_joint = wire_directs[w_index];
			}
		      else 
			{
			  found_joint = true;
			  found_neuron = true;
			  if (COMMENTS)
			    {cout << "Nothing on this run vSN" << endl;}
			}
		    }
		}
	    }
	  from_sensor = false;
	}
      // else neuron iteration
      else if (!from_sensor)
	{
	  // Go through all built neurons
	  for (int i=0; i < built_neurons.size(); i++)
	    {
	      // global index of built neuron
	      n_global = built_neurons[i][0];
	      //if it has free outputs, build a wire from it
	      if (neuron_outputs[n_global] > used_n_outputs[i])
		{
		  // if to_joint
		  if (to_joint)
		    {
		      i_hold = j_index;
		      // if not an empty slot in this joint
		      while (!(joint_inputs[built_joints[j_index]] > used_j_inputs[j_index]))
			{
			  // look in others
			  j_index++;
			  // keep looking
			  if (j_index >= built_joints.size())
			    {j_index = 0;}
			  // until you go through once
			  if (j_index == i_hold)
			    { found_joint = false;
			      break;}
			}
		      // If you find a good joint
		      if (found_joint)
			{
			  // set up wire
			  v_holder.push_back(w_index);
			  v_holder.push_back(n_global);
			  v_holder.push_back(built_joints[j_index]);
			  v_holder.push_back(0);
			  // build it
			  built_s_wires.push_back(v_holder);
			  if (COMMENTS)
			    {cout << "Built Wire--NJa: " << v_holder[0] << endl;}
			  used_j_inputs[j_index]++;
			  j_index++;
			  if (j_index >= built_joints.size())
			    {j_index = 0;}
			}
		      // If you don't find a good joint
		      else  
			{
			  i_hold = n_index;
			  // look for a good neuron
			  while (!(neuron_inputs[built_neurons[n_index][0]] > used_n_inputs[n_index]))
			    {
			      n_index++;
			      if (n_index >= built_neurons.size())
				{n_index = 0;}
			      if (n_index==i_hold)
				{ found_neuron = false;
				  break;}
			    }
			  // If you find a good neuron
			  if (found_neuron)
			    {
			      // set up wire
			      v_holder.push_back(w_index);
			      v_holder.push_back(n_global);
			      v_holder.push_back(built_neurons[n_index][0]);
			      v_holder.push_back(1);
			      // build it
			      built_s_wires.push_back(v_holder);
			      if (COMMENTS)
				{cout << "Built Wire--NNb " << v_holder[0] << endl;}
			      used_n_inputs[n_index]++;
			      n_index++;
			      if (n_index >= built_neurons.size())
				{n_index=0;}
			    }
			}
		      // and get ready for next step
		      if (found_joint||found_neuron)
			{
			  if (COMMENTS)
			    {cout << "test--NJ" << endl;}
			  v_holder.clear();
			  used_n_outputs[i]++;
			  w_index++;
			  if (w_index >= wire_total)
			    {break;}
			  to_joint = wire_directs[w_index];
			}
		      else 
			{
			  found_joint = true;
			  found_neuron = true;
			  if (COMMENTS)
			    {cout << "Nothing on this run vNJ" << endl;}
			}
		    }
		  // Or you look for a neuron first
		  else //this
		    {
		      i_hold = n_index;
		      // look for a good neuron
		      while (!(neuron_inputs[built_neurons[n_index][0]] > used_n_inputs[n_index]))
			{
			  n_index++;
			  if (n_index >= built_neurons.size())
			    {n_index = 0;}
			  if (n_index==i_hold)
			    { found_neuron = false;
			      break;}
			}
		      // If you find a good neuron
		      if (found_neuron)
			{
			  // set up wire
			  v_holder.push_back(w_index);
			  v_holder.push_back(n_global);
			  v_holder.push_back(built_neurons[n_index][0]);
			  v_holder.push_back(1);
			  // build it
			  built_s_wires.push_back(v_holder);
			  if (COMMENTS)
			    {cout << "Built Wire--NNa: " << v_holder[0] << endl;}
			  used_n_inputs[n_index]++;
			  n_index++;
			  if (n_index >= built_neurons.size())
			    {n_index=0;}
			}
		      // If you don't find a good neuron
		      else  
			{
			  // look for a joint instead
			  i_hold = j_index;
			  // if not an empty slot in this joint
			  while (!(joint_inputs[built_joints[j_index]] > used_j_inputs[j_index]))
			    {
			      // look in others
			      j_index++;
			      // keep looking
			      if (j_index >= built_joints.size())
				{j_index = 0;}
			      // until you go through once
			      if (j_index == i_hold)
				{ found_joint = false;
				  break;}
			    }
			  // If you find a good joint
			  if (found_joint)
			    {
			      // set up wire
			      v_holder.push_back(w_index);
			      v_holder.push_back(n_global);
			      v_holder.push_back(built_joints[j_index]);
			      v_holder.push_back(0);
			      // build it
			      built_s_wires.push_back(v_holder);
			      if (COMMENTS)
				{cout << "Built Wire--NJb " << v_holder[0] << endl;}
			      used_j_inputs[j_index]++;
			      j_index++;
			      if (j_index >= built_joints.size())
				{j_index = 0;}
			    }
			}
		      // and get ready for next step
		      if (found_joint||found_neuron)
			{
			  if (COMMENTS)
			    {cout << "test--NN" << endl;}
			  v_holder.clear();
			  used_n_outputs[i]++;
			  w_index++;
			  if (w_index >= wire_total)
			    {break;}
			  to_joint = wire_directs[w_index];
			}
		      else 
			{
			  found_joint = true;
			  found_neuron = true;
			  if (COMMENTS)
			    {cout << "Nothing on this run vNN" << endl;}
			}
		    }
		}
	    }
	  from_sensor = true;
	}
    }

  if (COMMENTS)
    {
      cout << endl;
      cout << "Wires Total: " << wire_total << endl;
      cout << "Joint Inputs: " << input_j_total << endl;
      cout << "Used Joint Inputs: " << used_part_counter(used_j_inputs) << endl; 
      cout << "Neuron Inputs: " << input_n_total << endl;
      cout << "Used Neuron Inputs: " << used_part_counter(used_n_inputs) << endl;
      cout << "Sensor Ouputs: " << output_s_total << endl;
      cout << "Used Sensor Outputs: " << used_part_counter(used_s_outputs) << endl;
      cout << "Neuron Ouputs: " << output_n_total << endl;
      cout << "Used Neuron Outputs: " << used_part_counter(used_n_outputs) << endl;  
    }

  if (COMMENTS)
    {
      cout << endl << built_s_wires.size() << " Wires from Sensors" << endl << endl;
      
      for (int i=0; i<built_s_wires.size(); i++)
	{
	  for (int j=0; j<built_s_wires[i].size(); j++)
	    {
	      cout << built_s_wires[i][j] << ',';
	    }
	  cout << endl;
	}
      
      cout << endl << built_n_wires.size() << " Wires from Neurons" << endl << endl;
      
      for (int i=0; i<built_n_wires.size(); i++)
	{
	  for (int j=0; j<built_n_wires[i].size(); j++)
	    {
	      cout << built_n_wires[i][j] << ',';
	    }
	  cout << endl;
	}
    }

   //========================== Build Wire Matrices ========================================
   
   d_hold = 0;
   vector<long double> dv_holder;
   
   // From sensor to joints
   for(int i=0;i<built_sensors.size();i++)
     {
       for(int j=0;j<built_joints.size();j++)
	 {
	   for(int k=0;k<built_s_wires.size();k++)
	     {
	       if ((built_s_wires[k][1]==built_sensors[i][0])&&// comes from sensor i
		   (built_s_wires[k][2]==built_joints[j])&&// goes to joint j
		   (built_s_wires[k][3]==0)) //wire goes to joints
		 {
		   d_hold += wire_weights[built_s_wires[k][0]];
		 }
	     }
	   dv_holder.push_back(d_hold);
	   d_hold = 0;
	 }
       weights_s2j.push_back(dv_holder);
       dv_holder.clear();
     }
   // From neurons to joints
   for(int i=0;i<built_neurons.size();i++)
     {
       for(int j=0;j<built_joints.size();j++)
	 {
	   for(int k=0;k<built_n_wires.size();k++)
	     {
	       if ((built_n_wires[k][1]==built_neurons[i][0])&&// comes from neuron i
		   (built_n_wires[k][2]==built_joints[j])&&// goes to joint j
		   (built_n_wires[k][3]==0)) //wire goes to joints
		 {
		   d_hold += wire_weights[built_n_wires[k][0]];
		 }
	     }
	   dv_holder.push_back(d_hold);
	   d_hold = 0;
	 }
       weights_n2j.push_back(dv_holder);
       dv_holder.clear();
     }
   // From sensors to neurons
    for(int i=0;i<built_sensors.size();i++)
     {
       for(int j=0;j<built_neurons.size();j++)
	 {
	   for(int k=0;k<built_s_wires.size();k++)
	     {
	       if ((built_s_wires[k][1]==built_sensors[i][0])&&// comes from sensor i
		   (built_s_wires[k][2]==built_neurons[j][0])&&// goes to neuron j
		   (built_s_wires[k][3]==1)) //wire goes to neurons
		 {
		   d_hold += wire_weights[built_s_wires[k][0]];
		 }
	     }
	   dv_holder.push_back(d_hold);
	   d_hold = 0;
	 }
       weights_s2n.push_back(dv_holder);
       dv_holder.clear();
     }
    // From neurons to neurons
     for(int i=0;i<built_neurons.size();i++)
     {
       for(int j=0;j<built_neurons.size();j++)
	 {
	   for(int k=0;k<built_n_wires.size();k++)
	     {
	       if ((built_n_wires[k][1]==built_neurons[i][0])&&// comes from neuron i
		   (built_n_wires[k][2]==built_neurons[j][0])&&// goes to neuron j
		   (built_n_wires[k][3]==1)) //wire goes to neurons
		 {
		   d_hold += wire_weights[built_n_wires[k][0]];
		 }
	     }
	   dv_holder.push_back(d_hold);
	   d_hold = 0;
	 }
       weights_n2n.push_back(dv_holder);
       dv_holder.clear();
     }
		
     if (COMMENTS)
       {
	 cout << "Sensor to Joint Weights" << endl;
	 for (int j=0;j<built_joints.size();j++)
	   {
	     for(int i=0;i<built_sensors.size();i++)
	       {
		 cout << weights_s2j[i][j] << ", ";
	       }
	     cout << endl;
	   }
	 cout << endl;
	 
	 cout << "Neuron to Joints Weights" << endl;
	 for (int j=0;j<built_joints.size();j++)
	   {
	     for(int i=0;i<built_neurons.size();i++)
	       {
		 cout << weights_n2j[i][j] << ", ";
	       }
	     cout << endl;
	   }
	 cout << endl;
	 
	 cout << "Sensor to Neuron Weights" << endl;
	 for (int j=0;j<built_neurons.size();j++)
	   {
	     for(int i=0;i<built_sensors.size();i++)
	       {
		 cout << weights_s2n[i][j] << ", ";
	       }
	     cout << endl;
	   }
	 cout << endl;
	 
	 cout << "Neuron to Neuron Weights" << endl;
	 for (int j=0;j<built_neurons.size();j++)
	   {
	     for(int i=0;i<built_neurons.size();i++)
	       {
		 cout << weights_n2n[i][j] << ", ";
	       }
	     cout << endl;
	   }
	 cout << endl;
       }     
}


// Set-up GUI for step-simulation 
void BasicWorld::clientMoveAndDisplay ()
{
  if (drawGraphics)
    {glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);}
  
  //simple dynamics world doesn't handle fixed-time-stepping
  /*
  float ms = getDeltaTimeMicroseconds();
  
  float minFPS = 50000.f/60.f;

  if (ms > minFPS)
    ms = minFPS;
  */
  // ================== Stepping through the world ====================
  if(m_dynamicsWorld)
    {
      if (!pause || (pause && oneStep))
	{
	  //reset touches 
	  for (int i=0;i<touches.size();i++)
	    {
	      touches[i] = 0;
	    }
	  for (int i=0;i<sensor_touches.size();i++)
	    {
	      sensor_touches[i] = 0;
	    }
	  
	  //m_dynamicsWorld->stepSimulation(ms/50000.f);
	  m_dynamicsWorld->stepSimulation(btScalar(1.)/btScalar(60.));
	  
	  if(drawGraphics)
	    {m_dynamicsWorld->debugDrawWorld();}
	 

	  if(RUNCOMMENTS)
	    {
	      cout << "Touches: ";
	      for (int i=0; i<touches.size(); i++)
		{
		  cout << touches[i] << ", ";
		}
	      cout << endl;
	    }
	  
	  //cout << "Setup sensor_touches calculations" << endl;
	 
	  if (RUNCOMMENTS)
	    {cout << "About to calculate sensor_touches" << endl;}
 
	  // This makes sensor_touches = 1 only if it touches on the right part of the body part
	  //for every sensor_touch[]
	  for (int i=0; i<sensor_touches.size(); i++)
	    {
	      if (RUNCOMMENTS)
		{cout << "Sensor " << i << ":: ";}
	      // if a body associated with that sensor touched
	      if (touches[body_touches[built_sensors[i][1]]]==1)
		{
		  if (RUNCOMMENTS)
		    {cout << "Body " << body_touches[built_sensors[i][1]] << " touched" << endl;}
		  //bps_index is the index of the body blueprint vectors.
		  bps_index = built_sensors[i][1];
		  //body_touches value is one more than the m_bodyparts index, b/c touch value for a body is one greater than the real index, b/c ground has touch index 0 but is not in m_bodyparts.
		  bps_built = body_touches[bps_index] - 1;
		  the_size = body_sizes[bps_index];
		  //the_body_pos = m_bodyparts[bps_built]->getCenterOfMassPosition();
		  bp_x = m_bodyparts[bps_built]->getCenterOfMassPosition().x();
		  bp_y = m_bodyparts[bps_built]->getCenterOfMassPosition().y();
		  bp_z = m_bodyparts[bps_built]->getCenterOfMassPosition().z();
		  //the_touch_pos = (PointWorldToLocal(bps_index, touchPoints[bps_built]));
		  t_x = touchPoints[bps_built].x();
		  t_y = touchPoints[bps_built].y();
		  t_z = touchPoints[bps_built].z();
		   // Sensor position
		  sensor_num = built_sensors[i][2];
		  sp_x = bp_x + (the_size * body_s_locs[bps_index][sensor_num][0]);
		  sp_y = bp_y + (the_size * body_s_locs[bps_index][sensor_num][1]);
		  sp_z = bp_z + (the_size * body_s_locs[bps_index][sensor_num][2]);
		  
		  if (((t_x <= (sp_x + sensor_area))&&
		       (t_y <= (sp_y + sensor_area))&&
		       (t_z <= (sp_z + sensor_area)))&&
		      ((t_x >= (sp_x - sensor_area))&&
		       (t_y >= (sp_y - sensor_area))&&
		       (t_z >= (sp_z - sensor_area))))
		    {
		      if (RUNCOMMENTS)
			{cout << "At the right place" << endl;}
		      sensor_touches[i]=1;
		    }
		  else
		    {
		      if (RUNCOMMENTS)
			{cout << "At the wrong place" << endl;}
		      sensor_touches[i]=0;
		    }
		}
	      else
		{
		  if (RUNCOMMENTS)
		    {cout << "Body " << body_touches[built_sensors[i][1]] << " didn't touch" << endl;}
		  sensor_touches[i]=0;
		}
	    }
	 
	  	  if(RUNCOMMENTS)
	    {
	      cout << "Sensor Touches: ";
	      for (int i=0; i<sensor_touches.size(); i++)
		{
		  cout << sensor_touches[i] << ", ";
		}
	      cout << endl;
	      cout << "Built Sensors & Bodys: ";
	      for (int i=0; i<built_sensors.size(); i++)
		{
		  cout << built_sensors[i][0] << ", " << body_touches[built_sensors[i][1]] << "; ";
		}
	      cout << endl;
	    }
 
	  // this comment doesn't apply anymore
	  // offset by 1 b/c touches[0] is ground
	  

	  // and reverse order b/c that's how matrix multiplication works with forloops
	  // First do Sensor to Neurons
	  for (int j=0;j<built_neurons.size();j++)
	    {
	      for (int i=0;i<built_sensors.size();i++)
		{
		  d_hold += sensor_touches[i] * weights_s2n[i][j];
		}
	      output_s2n.push_back(d_hold);
	      d_hold = 0;
	    }
	  // Second is Neurons to Neurons
	  for (int j=0;j<built_neurons.size();j++)
	    {
	      for (int i=0;i<output_s2n.size();i++)
		{
		  d_hold += output_s2n[i] * weights_n2n[i][j];
		}
	      output_n2n.push_back(d_hold);
	      d_hold = 0;
	    }
	  // Third is Sensors to Joints
	   for (int j=0;j<built_joints.size();j++)
	    {
	      for (int i=0;i<built_sensors.size();i++)
		{
		  d_hold += sensor_touches[i] * weights_s2j[i][j];
		}
	      output_s2j.push_back(d_hold);
	      d_hold = 0;
	    }
	  // Last is Neurons to Joint
	   for (int j=0;j<built_joints.size();j++)
	     {
	       for (int i=0;i<built_neurons.size();i++)
		 {
		   d_hold += output_n2n[i] * weights_n2j[i][j];
		 }
	       output_n2j.push_back(d_hold);
	       d_hold = 0;
	     }
	   
      	   if (RUNCOMMENTS)
	     {
	       cout << "Sensor to Joints Outputs" << endl;
	       for (int i=0; i<built_joints.size();i++)
		 {
		   cout << output_s2j[i] << ", ";
		 }
	       cout << endl;
	       cout << "Neuron to Joints Outputs" << endl;
	       for (int i=0; i<built_joints.size();i++)
		 {
		   cout << output_n2j[i] << ", ";
		 }
	       cout << endl;
	       cout << endl;
	     }
	     
	   // Combine both outputs and actuate joints
	   for (int i=0;i<built_joints.size();i++)
	     {
	       motor_command = output_s2j[i] + output_n2j[i];
	       if (RUNCOMMENTS)
		 { cout << "MotorCommand 1: " << motor_command << endl;}
	       motor_command = (2/(1+exp(-motor_command))-1);
	        if (RUNCOMMENTS)
		  { cout << "MotorCommand 2: " << motor_command << endl;}
	       motor_command = motor_command*360;
	        if (RUNCOMMENTS)
		  { cout << "MotorCommand 3: " << motor_command << endl;}
		if (output_s2j[i]!=0 && output_n2j[i]!=0)
		  {
		    ActuateJoint(built_joints[i], motor_command, btScalar(1.f)/btScalar(60.f));
		    //ActuateJoint(built_joints[i], motor_command, ms/50000.f);
		  }
		else 
		  { 
		    m_jointparts[built_joints[i]]->setMaxMotorImpulse(0);
		    m_jointparts[built_joints[i]]->enableMotor(false);
		  }
	     }
	   //cout << endl;
	   //clear holders
	   output_s2n.clear();
	   output_n2n.clear();
	   output_s2j.clear();
	   output_n2j.clear();
	   timeStep++;
	   //cout << timeStep << endl;
	   
	   if (drawGraphics)
	     {
	       if (timeStep >= 500)
		 {
		   Save_Position(true);
		   exit(0);
		 }
	     }
	   /*
	   if (timeStep >= 1000)
	     {
	       Save_Position(true);
	       exit(0);
	     }
	   */
	   oneStep = false;
	}
    }
  if (drawGraphics)
    {
      renderme();
      glFlush();
      glutSwapBuffers();
    }
}
  
void BasicWorld::displayCallback()
{
  if (drawGraphics)
    {
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); 
      renderme();
      if (m_dynamicsWorld)
	{m_dynamicsWorld->debugDrawWorld();}
      glFlush();
      glutSwapBuffers();
    }
}


void BasicWorld::keyboardCallback(unsigned char key, int x, int y)
{
  switch (key)
    {
    case 'p':
      {
	pause = (!pause);
      }
    case 's':
      {
	oneStep = true;
      }
    default:
      {
      DemoApplication::keyboardCallback(key, x, y);
      }
    }
}

// =================== Clean up Stage ===============================
void BasicWorld::exitPhysics()
{
 
  // Rigid Bodies
  // m_dynamicsWorld->removeRigidBody(fallRigidBody);
  //delete fallRigidBody->getMotionState();
  //delete fallRigidBody;

  //m_dynamicsWorld->removeRigidBody(groundRigidBody);
  //delete groundRigidBody->getMotionState();
  //delete groundRigidBody;
  
  // for my jointparts
  for (int i=0;i<m_jointparts.size();i++)
    {
      DestroyHinge(i);
    }

  // for my bodyparts
  for (int i=0;i<m_geomparts.size();i++)
    {
      DeleteObject(i);
    }

  /*
  //remove the rigidbodies from the dynamics world and delete them
  for (int i=m_dynamicsWorld->getNumCollisionObjects()-1; i>=0 ;i--)
    {
      btCollisionObject* obj = m_dynamicsWorld->getCollisionObjectArray()[i];
      btRigidBody* body = btRigidBody::upcast(obj);
      if (body && body->getMotionState())
	{
	  delete body->getMotionState();
	}
      m_dynamicsWorld->removeCollisionObject( obj );
      delete obj;
    }
  */

  // Ground
  delete fixedGround;
  delete groundShape;

  // World
  delete m_dynamicsWorld;
  delete m_solver;
  delete m_dispatcher;
  delete m_collisionConfiguration;
  delete m_broadphase;
}




