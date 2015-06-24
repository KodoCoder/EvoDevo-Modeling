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

	//keep the collision shapes, for deletion/cleanup
	btAlignedObjectArray<btCollisionShape*>	m_collisionShapes;
	// basic BP components
	btBroadphaseInterface*	m_broadphase;
	btCollisionDispatcher*	m_dispatcher;
	btConstraintSolver*	m_solver;
	btDefaultCollisionConfiguration* m_collisionConfiguration;
	btCollisionShape* groundShape;	
	btCollisionObject* fixedGround;
	// Control variables
	bool oneStep;
	bool pause; 
	// robot variables
	btAlignedObjectArray<btRigidBody*> m_bodyparts;
	btAlignedObjectArray<btCollisionShape*> m_geomparts;
	btAlignedObjectArray<btHingeConstraint*> m_jointparts;
	// Building variables
	//input 
	vector<string> body_strings;
	vector<string> joint_strings;
	vector<string> neuron_strings;
	vector<string> sensor_strings;
	vector<string> wire_strings;
	//holders to pass data through
	int i_hold;
	vector<long double> l_hold;
	vector<vector<long double > > dl_hold;
	string holder;
	int count = 0;
	long double d_hold;
	//Body-attribute lists
	vector<int> body_indexs;
	vector<string> body_kinds;
	vector<long double> body_sizes;
	vector<int> body_j_nums;
	vector<vector<vector<long double> > > body_j_locs;
	vector<int> body_n_nums;
	vector<int> body_s_nums;
	vector<vector<vector<long double> > > body_s_locs;
	vector<int> body_touches;
	//Joint-attribute lists
	vector<int> joint_indexs;
	vector<bool> joint_motors;
	vector<bool> joint_frees;
	vector<long double> joint_u_limits;
	vector<long double> joint_l_limits;
	vector<int> joint_inputs;
	//Neuron-attribute lists
	vector<int> neuron_indexs;
	vector<int> neuron_inputs;
	vector<int> neuron_outputs;
	//Sensor-attributes lists
	vector<int> sensor_indexs;
	vector<int> sensor_outputs;
	vector<int> sensor_touches;
	//Wire-attributes lists
	vector<int> wire_indexs;
	vector<long double> wire_weights;
	vector<bool> wire_directs;
	// Built part variables
	//builtbodies holds the global indexes of the built bodies in the order they were built
	vector<int> built_bodies;
	//built_joints holds the indexs of the built joints
	vector<int> built_joints;
	// holds index of sensors and neurons built, and the body index associated with it
	// inner vector of the form [global index of sensor/neuron, global index of associtated BP, sensor number of body]
	vector<vector<int> > built_sensors;
	vector<vector<int> > built_neurons;
	// inner vector of the form [index_of_wire, from (global part
	// index), to (global part index), to (part type--0 is joint, 1 is
	// neuron)]
	vector<vector<int> > built_s_wires;
	vector<vector<int> > built_n_wires;
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
	//Matrices
	vector<vector<long double> > weights_s2j;
	vector<vector<long double> > weights_n2j;
	vector<vector<long double> > weights_s2n;
	vector<vector<long double> > weights_n2n;
 public:
	//Collision Variables
	int * IDs;
	vector<int> touches;
	vector<btVector3> touchPoints;
	//Matrix Variables
	vector<long double> output_s2n;
	vector<long double> output_n2n;
	vector<long double> output_s2j;
	vector<long double> output_n2j;
	long double motor_command;
	//Display Variables
	bool drawGraphics; 
	unsigned long int timeStep;
	//public: 
	BasicWorld()
	{
	}
	virtual ~BasicWorld()
	{
	  exitPhysics();
	}
	
	void GrabBluePrints()
	{
	  ifstream blueprintFile("../python/blueprint.dat");
	  while (getline(blueprintFile, holder))
	    { 
	      // Set line as string to get data from
	      istringstream s(holder);     
	      // Skip empty lines
	      if (holder.empty())
		{
		  count ++;
		  continue;
		}
	      // Body Part Section
	      if (count < 8)
		{ 
		  // If empty skip to next section
		  if (holder[0] == 'E')
		    {
		      count = 8;
		      continue;
		    }
		  // Otherwise see where you are in count, and fill accordingly 
		  if (count==0 || count==3 || count==5 || count==6)
		    { 
		      while (getline(s, holder, ','))
			{
			  i_hold = stoi(holder);
			  if (count==0){body_indexs.push_back(i_hold);}
			  if (count==3){body_j_nums.push_back(i_hold);}
			  if (count==5){body_n_nums.push_back(i_hold);}
			  if (count==6){body_s_nums.push_back(i_hold);}
			}
		    }
		  if (count==1)
		    {
		      while (getline(s, holder, ','))
			{body_kinds.push_back(holder);}
		    }
		  if (count==2)
		    {
		      while (getline(s, holder, ','))
			{ d_hold = stod(holder) * .5;
			  body_sizes.push_back(d_hold);}
		    }
		  if (count==4 || count==7)
		    {
		      while (getline(s, holder,'|'))
			{
			  dl_hold.clear();
			  istringstream s2(holder);
			  while (getline(s2, holder, ';'))
			    {
			      l_hold.clear();
			      istringstream s3(holder);
			      while (getline(s3, holder, ','))
				{
				  d_hold = stod(holder);
				  l_hold.push_back(d_hold);
				}
			      dl_hold.push_back(l_hold);
			    }
			  if (count==4){body_j_locs.push_back(dl_hold);}
			  if (count==7){body_s_locs.push_back(dl_hold);}
			}
		    }
		  count++;
		  continue;
		}
	      // Joint Part Section
	      else if ((count > 8) && (count < 15))
		{
		  if (holder[0] == 'E')
		    { 
		      count = 15;
		      continue;
		    }
		  if (count==9)
		    {
		      while (getline(s, holder, ','))
			{
			  i_hold = stoi(holder);
			  joint_indexs.push_back(i_hold);
			}
		    }
		  if (count==10||count==11)
		    {
		      while (getline(s, holder, ','))
			{
			  if (holder[0]=='T')
			    { if (count==10)
				{joint_motors.push_back(true);}
			      if (count==11)
				{joint_frees.push_back(true);}
			    }
			  if (holder[0]=='F')
			    { if (count==10)
				{joint_motors.push_back(false);}
			      if (count==11)
				{joint_frees.push_back(false);}
			    }
			}
		    }
		  if (count==12||count==13)
		    {
		      while (getline(s, holder, ','))
			{
			  d_hold = stod(holder);
			  if (count==12)
			    {joint_u_limits.push_back(d_hold);}
			  if (count==13)
			    {joint_l_limits.push_back(d_hold);}
			}
		    }
		  if (count==14)
		    while (getline(s, holder, ','))
		      {
			i_hold = stoi(holder);
			joint_inputs.push_back(i_hold);
		      }
		  count++;
		  continue;
		}
	      // Neuron Part Section
	      else if ((count > 15) && (count < 19))
		{
		  if (holder[0] == 'E')
		    {
		      count = 19;
		      continue;
		    }
		  while (getline(s, holder, ','))
		    {
		      i_hold = stoi(holder);
		      if (count==16)
			{neuron_indexs.push_back(i_hold);}
		      if (count==17)
			{neuron_inputs.push_back(i_hold);}
		      if (count==18)
			{neuron_outputs.push_back(i_hold);}
		    }
		  count ++;
		  continue;
		}
	      // Sensor Part Section 
	      else if ((count > 19) && (count < 22))
		{ 
		  if (holder[0] == 'E')
		    {
		      count = 22;
		      continue;
		    }
		  if (count==20)
		    {
		      while (getline(s, holder, ','))
			{ i_hold = stoi(holder);
			  sensor_indexs.push_back(i_hold);}
		    }
		  if (count==21)
		    {
		      while (getline(s, holder, ','))
			{ i_hold = stoi(holder);
			  sensor_outputs.push_back(i_hold);}
		    }
		  count ++;
		  continue;
		}
	      // Wire Part Section
	      else if ((count > 22) && (count < 26))
		{
		  if (holder[0] == 'E')
		    {
		      count = 26;
		      continue;
		    }
		  if (count==23)
		    {
		      while (getline(s, holder, ','))
			{ i_hold = stoi(holder);
			  wire_indexs.push_back(i_hold);}
		    }
		  if (count==24)
		    {
		      while (getline(s, holder, ','))
			{ d_hold = stod(holder);
			  wire_weights.push_back(d_hold);}
		    }
		  if (count==25)
		    {
		      while (getline(s, holder, ','))
			{ 
			  if (holder[0]=='T')
			    { wire_directs.push_back(true);}
			  if (holder[0]=='F')
			    { wire_directs.push_back(false);}
			}
		    }
		  count ++;
		  continue;
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
