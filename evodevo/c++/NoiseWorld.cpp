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
#include "NoiseWorld.h"

#define COMMENTS false
#define RUNCOMMENTS false
#define DEGS_TO_RADS 3.141592653589793 / 180.f

//g++ -std=gnu++11 -g -v -I/root/sim/bullet-2.82-r2704/Demos/OpenGL/ -I/root/sim/bullet-2.82-r2704/src/ ./main.cpp -L/root/sim/bullet-build/Demos/OpenGl/ -L/root/sim/bullet-build/Demos/OpenGL/ -L/root/sim/bullet-build/src/BulletDynamics/ -L/root/sim/bullet-build/src/BulletCollision/ -L/root/sim/bullet-build/src/LinearMath -lOpenGLSupport -lGL -lGLU -lglut -lBulletDynamics -lBulletCollision -lLinearMath -o ./app

// Setup Collision Callback

static NoiseWorld* noiseWorld;

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
  
  noiseWorld->touches[*ID1] = 1;
  noiseWorld->touches[*ID2] = 1;
  noiseWorld->touchesPoints[*ID1] = cp.m_positionWorldOnB;
  noiseWorld->touchesPoints[*ID2] = cp.m_positionWorldOnB;

  return true;
}


// Initialize World

void NoiseWorld::initPhysics()
{
  //collision stuff
  noiseWorld = this;
  gContactProcessedCallback = myContactProcessedCallback;

  // ============= Getting, Manipulating, and Storing Blueprints ====================

  timeStep = 0;
  pause = false;
  oneStep = false;     
  stepTime = btScalar(1.)/btScalar(60.);
  
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


  // Files for part blueprints
  string bodyFile ("../io/body_blueprints_file.dat");
  string jointFile ("../io/joint_blueprints_file.dat");
  string sensorFile ("../io/sensor_blueprints_file.dat");
  string s2nFile ("../io/s2n_blueprint_file.dat");
  string n2nFile ("../io/n2n_blueprint_file.dat");
  string s2jFile ("../io/s2j_blueprint_file.dat");
  string n2jFile ("../io/n2j_blueprint_file.dat");

  // Create ground, spheres, joints

  bodys = UseBodyBlueprints(bodyFile);
  joints = UseJointBlueprints(jointFile);

  /*
  IDs = new int [bodys.size()+1]; 
  touches = new int [body.sizes()+1];
  touchesPoints = new btVector3 [body.sizes()+1];
  */
  
  m_bodyparts.clear();
  m_bodyparts.reserve(bodys.size());
  m_geomparts.clear();
  m_geomparts.reserve(bodys.size()+1);
  m_geomparts.clear();
  m_jointparts.reserve(joints.size());

  IDs = new int [bodys.size()+1]; 
  touches.clear();
  touches.reserve(bodys.size()+1);
  touchesPoints.clear();
  touchesPoints.reserve(bodys.size()+1);

  for (int i=0; i<(bodys.size()+1); i++)
    {
      IDs[i] = i;
      touches.push_back(0);
      touchesPoints.push_back(btVector3(0.,0.,0.));
    }

  CreateGround(0);
  
  //bodys[0].printSelf();
  CreateSphere(bodys[0].id, bodys[0].x, bodys[0].y, bodys[0].z, bodys[0].size);
  
  for (int i=0; i<joints.size(); i++)
    {
      //bodys[i+1].printSelf();
      CreateSphere(bodys[i+1].id, bodys[i+1].x, bodys[i+1].y, bodys[i+1].z, bodys[i+1].size);
      //joints[i].printSelf();
      CreateHinge(joints[i].id, joints[i].base_body, joints[i].other_body,
		  joints[i].px, joints[i].py, joints[i].pz, 
		  joints[i].ax, joints[i].ay, joints[i].az, 
		  joints[i].lower_limit, joints[i].upper_limit, joints[i].motor);
    }

  // Create ANN

  sensors = UseSensorBlueprints(sensorFile);
  /*
  for (int i; i<sensors.size(); i++)
    {
      sensors[i].printSelf();
    }
  */
  sensorTouches.clear();
  sensorTouches.reserve(sensors.size());
  for (int i=0; i<sensors.size(); i++)
    {
      sensorTouches.push_back(0);
    }


  //sensorTouches = vector<int> (0, sensors.size());
  weights_s2n = UseMatrixBlueprints(s2nFile);
  weights_n2n = UseMatrixBlueprints(n2nFile);
  weights_s2j = UseMatrixBlueprints(s2jFile);
  weights_n2j = UseMatrixBlueprints(n2jFile);

  /*
  cout << endl;
  for (int i=0; i<weights_s2n.size(); i++)
    {
      for (int j=0; j<weights_s2n[i].size(); j++)
	{
	  cout << weights_s2n[i][j] << ", ";
	}
      cout << endl;
    }
  cout << endl;

  for (int i=0; i<weights_n2n.size(); i++)
    {
      for (int j=0; j<weights_n2n[i].size(); j++)
	{
	  cout << weights_n2n[i][j] << ", ";
	}
      cout << endl;
    }
  cout << endl;

  for (int i=0; i<weights_s2j.size(); i++)
    {
      for (int j=0; j<weights_s2j[i].size(); j++)
	{
	  cout << weights_s2j[i][j] << ", ";
	}
      cout << endl;
    }
  cout << endl;

  for (int i=0; i<weights_n2j.size(); i++)
    {
      for (int j=0; j<weights_n2j[i].size(); j++)
	{
	  cout << weights_n2j[i][j] << ", ";
	}
      cout << endl;
    }
  cout << endl;
  */

}
  

// Set-up GUI for step-simulation 
void NoiseWorld::clientMoveAndDisplay ()
{
  if (drawGraphics)
    {glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);}

  // ================== Stepping through the world ====================
  if(m_dynamicsWorld)
    {
      if (!pause || (pause && oneStep))
	{
	  //reset touches 
	  for (int i=0;i<touches.size();i++)
	    {
	      touches[i] = 0;
	      touchesPoints[i] = btVector3(0.,0.,0.);
	    }
	  for (int i=0;i<sensorTouches.size();i++)
	    {
	      sensorTouches[i] = 0;
	    }
	  
	  m_dynamicsWorld->stepSimulation(stepTime);
	  
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
	  
	  if (RUNCOMMENTS)
	    {cout << "About to calculate sensorTouches" << endl;}
 
	  // This makes sensorTouches = 1 only if it touches on the right part of the body part
	  for (int i=0; i<sensors.size(); i++)
	    {	      
	      sensor_body_id = sensors[i].body_id;
	      sensor_touches_id = sensor_body_id + 1;
	      if (touches[sensor_touches_id]==1)
		{
		  // Body position
		  bp_x = m_bodyparts[sensor_body_id]->getCenterOfMassPosition().x();
		  bp_y = m_bodyparts[sensor_body_id]->getCenterOfMassPosition().y();
		  bp_z = m_bodyparts[sensor_body_id]->getCenterOfMassPosition().z();
		  // Sensor position
		  the_size = bodys[sensor_body_id].size;
		  sp_x = bp_x + (the_size * sensors[i].x);
		  sp_y = bp_y + (the_size * sensors[i].y);
		  sp_z = bp_z + (the_size * sensors[i].z);
		  // Touched
		  t_x = touchesPoints[sensor_touches_id].x();
		  t_y = touchesPoints[sensor_touches_id].y();
		  t_z = touchesPoints[sensor_touches_id].z();		 
		  if (((t_x <= (sp_x + sensor_area))&&
		       (t_y <= (sp_y + sensor_area))&&
		       (t_z <= (sp_z + sensor_area)))&&
		      ((t_x >= (sp_x - sensor_area))&&
		       (t_y >= (sp_y - sensor_area))&&
		       (t_z >= (sp_z - sensor_area))))
		    {
		      sensorTouches[i]=1;
		    }
		}
	    }
       
	  // Calculate activation through ANN
	  //cout << "output_s2n" << endl;
	  output_s2n = CalculateLayer(weights_s2n, sensorTouches);
	  
	  //cout << "output_n2n" << endl;
	  output_n2n = CalculateLayer(weights_n2n, output_s2n);

	  //cout << "output_s2j" << endl;
	  output_s2j = CalculateLayer(weights_s2j, sensorTouches);

	  //cout << "output_n2j" << endl;
	  output_n2j = CalculateLayer(weights_n2j, output_n2n);	   

	  
	  // Combine both outputs and actuate joints
	  for (int i=0;i<joints.size();i++)
	    {
	      if (joints[i].motor)
		{
		  motor_command = output_s2j[i] + output_n2j[i];
		  if (RUNCOMMENTS)
		    { cout << "MotorCommand 1: " << motor_command << endl;}
		  
		  motor_command = (2/(1+exp(-motor_command))-1);
		  if (RUNCOMMENTS)
		    { cout << "MotorCommand 2: " << motor_command << endl;}

		  motor_command = motor_command * DEGS_TO_RADS;
		  if (RUNCOMMENTS)
		    { cout << "MotorCommand 3: " << motor_command << endl;}
		 
		  ActuateJoint(joints[i].id, motor_command, stepTime);
		}
	    }
	  
	  timeStep++;	  

	  if (drawGraphics)
	    {
	      if (timeStep >= 500)
		{
		  Save_Position(true);
		  exit(0);
		}
	    }

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
  
void NoiseWorld::displayCallback()
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


void NoiseWorld::keyboardCallback(unsigned char key, int x, int y)
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
void NoiseWorld::exitPhysics()
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
      DeleteHinge(i);
    }

  DeleteGround();

  // for my bodyparts
  for (int i=0;i<m_bodyparts.size();i++)
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
  
  /*
  delete weights_n2j;
  delete weights_s2j;
  delete weights_n2n;
  delete weights_s2n;
  
  delete sensorTouches;
  delete sensors;

  delete touchesPoints;
  delete touches;
  delete IDs;

  delete joints;
  delete bodys;
  */

  // Ground
  //delete fixedGround;
  //delete groundShape;

  // World
  delete m_dynamicsWorld;
  delete m_solver;
  delete m_dispatcher;
  delete m_collisionConfiguration;
  delete m_broadphase;
}




