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


class BodyPart { 
 public:
  int id;
  long double x, y, z;
  long double size;
  void readBlueprint(istringstream&);
  void printSelf();
};

void BodyPart::readBlueprint (istringstream &blueprintRow) {
    string val;
    for (int i=0; i<5; i++) {
      getline(blueprintRow, val, ',');
      if (i==0) { id = stoi(val); }
      if (i==1) { x = stod(val); }
      if (i==2) { y = stod(val); }
      if (i==3) { z = stod(val); }
      if (i==4) { size = stod(val); }
    }
}

void BodyPart::printSelf() {
  cout << "Body" << endl;
  cout << id << ", " << x << ", " << y << ", " << z << ", " << size << endl;
}
  

class JointPart {
 public:
  int id, base_body, other_body;
  long double ax, ay, az, px, py, pz;
  btScalar lower_limit, upper_limit;
  bool motor;
  void readBlueprint(istringstream&);
  void printSelf();
};

void JointPart::readBlueprint (istringstream &blueprintRow) {
  string val;
  for (int i=0; i<12; i++) {
    getline(blueprintRow, val, ',');
    if (i==0) { id = stoi(val); }
    if (i==1) { base_body = stoi(val); }
    if (i==2) { other_body = stoi(val); }
    if (i==3) { px = stod(val); }
    if (i==4) { py = stod(val); }
    if (i==5) { pz = stod(val); }
    if (i==6) { ax = stod(val); }
    if (i==7) { ay = stod(val); }
    if (i==8) { az = stod(val); }
    if (i==9) { lower_limit = stod(val); }
    if (i==10) { upper_limit = stod(val); }
    if (i==11) { 
      if (val[0]=='T') { motor = true; }
      if (val[0]=='F') { motor = false; }
    }
  }
}

void JointPart::printSelf() {
  cout << "Joint" << endl;
  cout << id << ", " << base_body << ", " << other_body << endl;
  cout << px << ", "<< py << ", "<< pz << endl;
  cout << ax << ", " << ay << ", " << az << endl;
  cout << lower_limit << ", " << upper_limit << ", " << motor << endl;
}


class SensorPart
{
 public:
  int id, body_id;
  long double x, y, z;
  void readBlueprint(istringstream&);
  void printSelf();
};

void SensorPart::readBlueprint (istringstream &blueprintRow) {
  string val;
  for (int i=0; i<5; i++) {
    getline(blueprintRow, val, ',');
    if (i==0) { id = stoi(val); }
    if (i==1) { body_id = stoi(val); }
    if (i==3) { x = stod(val); }
    if (i==3) { y = stod(val); }
    if (i==4) { z = stod(val); }
  }
}

void SensorPart::printSelf() {
  cout << "Sensor" << endl;
  cout << id << ", " << body_id << ", " << x << ", " << y << ", " << z << endl;
}


class NoiseWorld : public GlutDemoApplication
{
	// ---Basic BP components---
	btBroadphaseInterface*	m_broadphase;
	btCollisionDispatcher*	m_dispatcher;
	btConstraintSolver*	m_solver;
	btDefaultCollisionConfiguration* m_collisionConfiguration;
	btCollisionShape* groundShape;	
	btCollisionObject* fixedGround;
	// ---Control variables---
	bool oneStep;
	bool pause;
	btScalar stepTime;

	// ---Bullet Physics constructs for robot parts---
	btAlignedObjectArray<btRigidBody*> m_bodyparts;
	btAlignedObjectArray<btCollisionShape*> m_geomparts;
	btAlignedObjectArray<btHingeConstraint*> m_jointparts;
	// don't need \/ this \/ one because of m_geomparts probably
	// btAlignedObjectArray<btCollisionShape*>	m_collisionShapes;

	// ---Sensor_touches variables---
	int sensor_body_id;
	int sensor_touches_id;
	long double the_size;
	const btScalar sensor_area = .2;
	btScalar bp_x;
	btScalar bp_y;
	btScalar bp_z;
	btScalar sp_x;
	btScalar sp_y;
	btScalar sp_z;
	btScalar t_x;
	btScalar t_y;
	btScalar t_z;
	// ---ANN outputs---
	vector<long double> output_s2n;
	vector<long double> output_n2n;
	vector<long double> output_s2j;
	vector<long double> output_n2j;
	long double motor_command;
 public:
	// ---Blueprint Variables---
	vector<BodyPart> bodys;
	vector<JointPart> joints;
	vector<SensorPart> sensors;
	vector<long double> sensorTouches;
	// ---ANN Matrices---
	vector<vector<long double> > weights_s2n;
	vector<vector<long double> > weights_n2n;	
	vector<vector<long double> > weights_s2j;
	vector<vector<long double> > weights_n2j;
	// ---Collision variables---
	int * IDs;
 	vector<int> touches;
	vector<btVector3> touchesPoints;
	// ---Display Variables---
	bool drawGraphics; 
	unsigned long int timeStep;

	// Methods
	NoiseWorld()
	{
	}
	virtual ~NoiseWorld()
	{
	  exitPhysics();
	}


	vector<BodyPart> UseBodyBlueprints(string filename)
	{
	  vector<BodyPart> bodyList;
	  string line;
	  ifstream blueprintFile(filename);
	  while (getline(blueprintFile, line))
	    {
	      istringstream constructInfo(line);
	      BodyPart part;
	      part.readBlueprint(constructInfo);
	      bodyList.push_back(part);
	    }
	  blueprintFile.close();
	  return bodyList;
	}


	vector<JointPart> UseJointBlueprints(string filename)
	{
	  vector<JointPart> jointList;
	  string line;
	  ifstream blueprintFile(filename);
	  while (getline(blueprintFile, line))
	    {
	      istringstream constructInfo(line);
	      JointPart part;
	      part.readBlueprint(constructInfo);
	      jointList.push_back(part);
	    }
	  blueprintFile.close();
	  return jointList;
	}
	  
	
	vector<SensorPart> UseSensorBlueprints(string filename)
	  {
	    vector<SensorPart> sensorList;
	    string line;
	    ifstream blueprintFile(filename);
	    while (getline(blueprintFile, line))
	      {
		istringstream constructInfo(line);
		SensorPart part;
		part.readBlueprint(constructInfo);
		sensorList.push_back(part);
	      }
	    blueprintFile.close();
	    return sensorList;
	  }

	
	vector<vector<long double > > UseMatrixBlueprints(string filename)
	  {
	    vector<vector<long double > > matrix;
	    vector<long double> row;
	    string line;
	    string element;
	    ifstream blueprintFile(filename);
	    //if (blueprintFile.peek() != std::ifstream::traits_type::eof())
	    while (getline(blueprintFile, line))
	      {
		istringstream lineStream(line);
		while (getline(lineStream, element, ','))
		  {
		    row.push_back(stod(element));
		  }
		matrix.push_back(row);
		row.clear();
	      }
	    return matrix;
	  }
		  
	  
	// building functions
	void CreateGround(int index)
	{
	  groundShape = new btStaticPlaneShape(btVector3(0, 1, 0), 1);
	  //m_collisionShapes.push_back(groundShape);
	  m_geomparts.push_back(groundShape);
	  
	  btTransform groundTransform;
	  groundTransform.setIdentity();
	  groundTransform.setOrigin(btVector3(0,-1,0));
	  
	  fixedGround = new btCollisionObject();
	  fixedGround->setCollisionShape(groundShape);
	  fixedGround->setWorldTransform(groundTransform);
	  fixedGround->setUserPointer(&(IDs[index]));
	  m_dynamicsWorld->addCollisionObject(fixedGround);  
	}
	

	void CreateSphere(int index, btScalar x, btScalar y, btScalar z, btScalar size)
	{
	  btCollisionShape* sphere = new btSphereShape(size);
	  //m_collisionShapes.push_back(sphere);
	  m_geomparts.push_back(sphere);
	  btTransform sphereTransform;
	  sphereTransform.setIdentity();
	  btVector3 position (x, y, z);
	  sphereTransform.setOrigin(position);
	  btScalar mass = 1;
	  bool isDynamic = (mass != 0.f);
	  btVector3 localInertia(0,0,0);
	  if (isDynamic)
	    {
	      sphere->calculateLocalInertia(mass, localInertia);
	      sphereTransform.setOrigin(position);
	      btDefaultMotionState* myMotionState = new btDefaultMotionState(sphereTransform);
	      btRigidBody::btRigidBodyConstructionInfo rbInfo(mass,myMotionState,sphere,localInertia);
	      m_bodyparts.push_back(new btRigidBody(rbInfo));
	      m_bodyparts[index]->setUserPointer(&(IDs[index+1])); 
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


	void CreateHinge(int index, int body1, int body2,
			 btScalar px, btScalar py, btScalar pz,
			 btScalar ax, btScalar ay, btScalar az,
			 btScalar lower, btScalar upper, bool motor)
	{
	  btVector3 position (px, py, pz);
	  btVector3 axis (ax, ay, az);
	  btVector3 locPoint1 = PointWorldToLocal(body1, position);
	  btVector3 locAxis1 = AxisWorldToLocal(body1, axis);
	  btVector3 locPoint2 = PointWorldToLocal(body2, position);
	  btVector3 locAxis2 = AxisWorldToLocal(body2, axis);
	  m_jointparts.push_back(new btHingeConstraint(*m_bodyparts[body1], *m_bodyparts[body2], 
						       locPoint1, locPoint2, locAxis1, locAxis2,
						       false));
	    m_jointparts[index]->setLimit(lower, upper);
	    m_dynamicsWorld->addConstraint(m_jointparts[index], true);
	    m_jointparts[index]->enableMotor(motor);
	  }


	void ActuateJoint(int jointIndex, double desiredAngle, double dt)
	{
	  //m_jointparts[jointIndex]->enableMotor(joints[jointIndex].motor);
	  m_jointparts[jointIndex]->setMaxMotorImpulse(.4);
	  m_jointparts[jointIndex]->setMotorTarget(desiredAngle, dt);
	}
	

	void DeleteGround()
	{
	  delete groundShape;
	  delete fixedGround;
	}


	void DeleteObject(int index)
	{
	  delete m_geomparts[index+1];
	  delete m_bodyparts[index];
	}


	void DeleteHinge(int index)
	{
	  delete m_jointparts[index];
	}

	vector<long double> CalculateLayer(vector<vector<long double > > matrix, 
					   vector<long double> dataIn)
	  {
	    //cout << matrix.size() << ',' << matrix[0].size() << endl;
	    //cout << dataIn.size() << endl;
	    long double d_hold (0);
	    vector<long double> output;
	    for (int j=0; j<matrix[0].size(); j++)
	      {
		d_hold = 0;
		for (int i=0; i<dataIn.size(); i++)
		  {
		    //cout << i << ", " << j << endl;
		    //cout << dataIn[i] << ", " << matrix[i][j] << endl;
		    d_hold += dataIn[i] * matrix[i][j];
		    //cout << endl << endl;
		  }
		output.push_back(d_hold);
	      }
	    return output;
	  }
	

	int Save_Position(bool completed)
	{
	  if (completed) 
	    {
	      btVector3 position = m_bodyparts[0]->getCenterOfMassTransform().getOrigin();
	      btScalar distance = sqrt(pow(position.getX(), 2) + pow(position.getZ(), 2));
	      ofstream fitsFile("../io/simulation_data.dat", ios::out);
	      fitsFile << distance << endl;
	      //fitsFile << built_joints.size()+1 << endl;
	      //fitsFile << built_joints.size() << endl;
	      //fitsFile << built_sensors.size() << endl;
	      //fitsFile << built_neurons.size() << endl;
	      //fitsFile << built_s_wires.size() + built_n_wires.size() << endl;
	      fitsFile.close();
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
		NoiseWorld* demo = new NoiseWorld;
		demo->myinit();
		demo->initPhysics();
		return demo;
	}	
};
      

  
  
