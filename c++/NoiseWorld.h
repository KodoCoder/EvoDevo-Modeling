#include "GL_ShapeDrawer.h"
#include "GlutDemoApplication.h"
//#include "LinearMath/btAlignedObjectArray.h"
#include "btBulletCollisionCommon.h"
#include "btBulletDynamicsCommon.h"
#include <string>
#include <vector>
#include <stdio.h>
#include <math.h>

class btBroadphaseInterface;
class btCollisionShape;
class btOverlappingPairCache;
class btCollisionDispatcher;
class btConstraintSolver;
struct btCollisionAlgorithmCreateFunc;
class btDefaultCollisionConfiguration;

using namespace std;

class BasicWorld : public GlutDemoApplication
{
	// basic BP components
	btBroadphaseInterface*	m_broadphase;
	btCollisionDispatcher*	m_dispatcher;
	btConstraintSolver*	m_solver;
	btDefaultCollisionConfiguration* m_collisionConfiguration;
	btCollisionShape* groundShape;	
	btCollisionObject* fixedGround;
	// ---Control variables---
	bool oneStep;
	bool pause; 
	// ---Bullet Physics constructs for robot parts---
	btAlignedObjectArray<btRigidBody*> m_bodyparts;
	btAlignedObjectArray<btCollisionShape*> m_geomparts;
	btAlignedObjectArray<btHingeConstraint*> m_jointparts;
	// don't need \/ this \/ one because of m_geomparts probably
	// btAlignedObjectArray<btCollisionShape*>	m_collisionShapes;

	// ---Blueprint variables---
	string holder;
	//Sensor_touches variables
	const btScalar sensor_area = .3;
	int bps_index;
	int bps_built;
	long double the_size;
	//btVector3 the_body_pos;
	btScalar bp_x;
	btScalar bp_y;
	btScalar bp_z;
	btScalar sp_x;
	btScalar sp_y;
	btScalar sp_z;
	int sensor_num;
	//btVector3 the_touch_pos;
	btScalar t_x;
	btScalar t_y;
	btScalar t_z;
	// ANN Matrices
	vector<vector<long double> > weights_s2j;
	vector<vector<long double> > weights_n2j;
	vector<vector<long double> > weights_s2n;
	vector<vector<long double> > weights_n2n;
 public:
	// ---Variables---
	// Collision
	int * IDs;
	vector<int> touches;
	vector<btVector3> touchPoints;
	// ANN outputs
	vector<long double> output_s2n;
	vector<long double> output_n2n;
	vector<long double> output_s2j;
	vector<long double> output_n2j;
	long double motor_command;
	// Display Variables
	bool drawGraphics; 
	unsigned long int timeStep;
	// ---Functions---
	BasicWorld()
	{
	}
	virtual ~BasicWorld()
	{
	  exitPhysics();
	}
	

	// GrabBluprints 
	void GrabBlueprints(filename)
	{
	  ifstream blueprintFile(filename);
	  while (getline(blueprintFile, holder))
	    {
	      while (getline(s, holder, ','))
		{
		}
	    }
	  blueprintFile.close();
	}
	  
	  
	// building functions
	void CreateGround(int index)
	{
	  groundShape = new btStaticPlaneShape(btVector3(0, 1, 0), 1);
	  m_collisionShapes.push_back(groundShape);
	  //m_collisionShapes[index] = groundShape;
	  
	  btTransform groundTransform;
	  groundTransform.setIdentity();
	  groundTransform.setOrigin(btVector3(0,-1,0));
	  
	  fixedGround = new btCollisionObject();
	  fixedGround->setCollisionShape(groundShape);
	  fixedGround->setWorldTransform(groundTransform);
	  fixedGround->setUserPointer(&(IDs[index]));
	  m_dynamicsWorld->addCollisionObject(fixedGround);  
	}

	/*
	  void CreateBox(int index, btVector3 origin, btScalar size)
	  {
	  btCollisionShape* box = new btBoxShape(btVector3(size,size,size));
	  m_collisionShapes.push_back(box);
	  // I don't think I need the below because of the above
	  //m_collisionShapes.push_back(box);
	  btTransform boxTransform;
	  boxTransform.setIdentity();
	  boxTransform.setOrigin(origin);
	  //Apparently all mass is supposed to be around 1
          //btScalar density = .23866348448;
	  //btScalar mass  = density * (size*2)*(size*2);
	  btScalar mass = 1;
	  bool isDynamic = (mass != 0.f);
	  btVector3 localInertia(0,0,0);
	  m_geomparts.push_back(box);
	  
	  if (isDynamic)
	    {
	      box->calculateLocalInertia(mass, localInertia);
	      boxTransform.setOrigin(origin);
	      btDefaultMotionState* myMotionState = new btDefaultMotionState(boxTransform);
	      btRigidBody::btRigidBodyConstructionInfo rbInfo(mass,myMotionState,box,localInertia);
	      m_bodyparts.push_back(new btRigidBody(rbInfo));
	      //
	      //If index is zero, make zero a 'buffer' ID for ground to take later
	      //
	      m_bodyparts[index]->setUserPointer( &(IDs[index+1]) ); 
	      // below is probably not needed
	      // m_bodyparts->setFriction(0.5);
	      // m_bodyparts[index]->setActivationState(DISABLE_DEACTIVATION);
	      m_dynamicsWorld->addRigidBody(m_bodyparts[index]);
	    }
	}
	*/
	
	void CreateSphere(int index, btScalar x, btScalar y, btScalar z, btScalar size)
	{
	  btCollisionShape* sphere = new btSphereShape(size);
	  m_collisionShapes.push_back(sphere);
	  //m_collisionShapes[index] = sphere;
	  btTransform sphereTransform;
	  sphereTransform.setIdentity();
	  sphereTransform.setOrigin(btVector3(x, y, z));
	  //Apparently all mass is supposed to be at/around 1
	  //btScalar m_pi = 3.14159265358979323846;
          //btScalar density = .23866348448;
	  //btScalar mass  = density * (4*m_pi/3) * size * size * size;
	  btScalar mass = 1;
	  bool isDynamic = (mass != 0.f);
	  btVector3 localInertia(0,0,0);
	  m_geomparts.push_back(sphere);
	  //m_geomparts[index] = sphere;
	  if (isDynamic)
	    {
	      sphere->calculateLocalInertia(mass, localInertia);
	      sphereTransform.setOrigin(btVector3(x,y,z));
	      btDefaultMotionState* myMotionState = new btDefaultMotionState(sphereTransform);
	      btRigidBody::btRigidBodyConstructionInfo rbInfo(mass,myMotionState,sphere,localInertia);
	      m_bodyparts.push_back(new btRigidBody(rbInfo));
	      //m_bodyparts[index] = new btRigidBody(rbInfo);
	      m_bodyparts[index]->setUserPointer(&(IDs[index+1])); 
	      //Above is for IDing collisions, below is probably not needed
	      m_bodyparts[index]->setFriction(0.8);
	      m_bodyparts[index]->setRollingFriction(0.5);
	      m_bodyparts[index]->setActivationState(DISABLE_DEACTIVATION);
	      m_dynamicsWorld->addRigidBody(m_bodyparts[index]);
	    }
	}
     

	btVector3 PointWorldToLocal(int bodyIndex, btVector3 &point)
	{
	  return m_bodyparts[bodyIndex]->getCenterOfMassTransform().inverse()(point);
	}

	btVector3 AxisWorldToLocal(int bodyIndex, btVector3 &axis)
	{
	  btTransform local1 =  m_bodyparts[bodyIndex]->getCenterOfMassTransform().inverse();
	  btVector3 myZero(0., 0., 0.);
	  local1.setOrigin(myZero);
	  return local1 * axis;
	}

	void CreateHinge(int index, int body1, int body2, btScalar point_x, btScalar point_y, btScalar point_z, btScalar axis_x, btScalar axis_y, btScalar axis_z, btScalar lower, btScalar upper, bool motor)
	  {
	    btVector3 point(point_x, point_y, point_z);
	    btVector3 axis(axis_x, axis_y, axis_z);
	    btVector3 locPoint1 = PointWorldToLocal(body1, point);
	    btVector3 locAxis1 = AxisWorldToLocal(body1, axis);
	    btVector3 locPoint2 = PointWorldToLocal(body2, point);
	    btVector3 locAxis2 = AxisWorldToLocal(body2, axis);
	    m_jointparts.push_back(new btHingeConstraint(*m_bodyparts[body1], *m_bodyparts[body2], locPoint1, locPoint2, locAxis1, locAxis2, false));
	    m_jointparts[index]->setLimit(lower, upper);
	    m_dynamicsWorld->addConstraint(m_jointparts[index], true);
	    m_jointparts[index]->enableMotor(motor);
	  }

	void ActuateJoint(int jointIndex, double desiredAngle, double dt)
	{
	  m_jointparts[jointIndex]->enableMotor(joint_motors[jointIndex]);
	  m_jointparts[jointIndex]->setMaxMotorImpulse(.4);
	  m_jointparts[jointIndex]->setMotorTarget(desiredAngle * 3.14159/180., dt);
	}
	
	void DeleteObject(int index)
	{
	  delete m_geomparts[index];
	  delete m_bodyparts[index];
	}

	void DestroyHinge(int index)
	{
	  delete m_jointparts[index];
	}

	void PrintTestI(vector<int> tested)
	{ 
	  for (int i=0; i<tested.size(); i++)
	    {
	      cout << tested[i] << ',';
	    }
	  cout << endl;
	}

	void PrintTestS(vector<string> tested)
	{ 
	  for (int i=0; i<tested.size(); i++)
	    {
	      cout << tested[i] << ',';
	    }
	  cout << endl;
	}

	void PrintTestD(vector<long double> tested)
	{ 
	  for (int i=0; i<tested.size(); i++)
	    {
	      cout << tested[i] << ',';
	    }
	  cout << endl;
	}

	void PrintTestB(vector<bool> tested)
	{ 
	  for (int i=0; i<tested.size(); i++)
	    {
	      if (tested[i])
		{ cout << "True" << ',';}
	      else
		{ cout << "False" << ',';}
	    }
	  cout << endl;
	}

	void PrintTest2(vector<vector<vector<long double > > > tested)
	{
	  for (int i=0; i<tested.size(); i++)
	    {
	      for (int j=0; j<tested[i].size(); j++)
		{
		  for (int k=0; k<3; k++)
		    {
		      cout << tested[i][j][k] << ',';
		    }
		  cout << ';';
		}
	      cout << '|';
	    }
	  cout << endl;
	}

	int used_part_counter(vector<int> listy)
	{
	  int accumy = 0;
	  for (int i=0;i<listy.size();i++)
	    {
	      accumy += listy[i];
	    }
	  return accumy;
	}

	int Save_Position(bool completed)
	{
	  if (completed) 
	    {
	      btVector3 position = m_bodyparts[0]->getCenterOfMassTransform().getOrigin();
	      btScalar distance = sqrt(pow(position.getX(), 2) + pow(position.getZ(), 2));
	      ofstream fitsFile("../python/fits.dat", ios::out);
	      fitsFile << distance << endl;
	      fitsFile << built_joints.size()+1 << endl;
	      fitsFile << built_joints.size() << endl;
	      fitsFile << built_sensors.size() << endl;
	      fitsFile << built_neurons.size() << endl;
	      fitsFile << built_s_wires.size() + built_n_wires.size() << endl;
	      fitsFile.close();
	      /*
	      cout << built_joints.size()+1 << endl;
	      cout << built_joints.size() << endl;
	      cout << built_sensors.size() << endl;
	      cout << built_neurons.size() << endl;
	      cout << built_s_wires.size() + built_n_wires.size() << endl;
	      */
	      return 0;
	    }
	  else 
	    { 
	      ofstream fitsFile("../python/fits.dat", ios::out);
	      fitsFile << 0 << endl;
	      fitsFile << 0 << endl;
	      fitsFile << 0 << endl;
	      fitsFile << 0 << endl;
	      fitsFile << 0 << endl;
	      fitsFile << 0 << endl;
	      fitsFile.close();
	      return 0;
	    } 
	}

	void initPhysics();

	void exitPhysics();

	virtual void clientMoveAndDisplay();

	virtual void displayCallback();

	virtual void keyboardCallback(unsigned char key, int x, int y);	
	
	static DemoApplication* Create()
	{
		BasicWorld* demo = new BasicWorld;
		demo->myinit();
		demo->initPhysics();
		return demo;
	}	
};
