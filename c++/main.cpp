#include "BasicWorld.cpp"
#include "GlutStuff.h"
#include "GLDebugDrawer.h"
#include "btBulletDynamicsCommon.h"

GLDebugDrawer	gDebugDrawer;

int main(int argc, char *argv[])

{
  BasicWorld demoApp;

  if (argc==0)
    {demoApp.drawGraphics = false;
    }
  else
    {demoApp.drawGraphics = true;}
  demoApp.initPhysics();
  demoApp.getDynamicsWorld()->setDebugDrawer(&gDebugDrawer);
  if(argc==0) 
    {
      while(demoApp.timeStep <= 500) 
	{
	  demoApp.clientMoveAndDisplay();
	}
      return demoApp.Save_Position(true);
    }
  else 
    {
      return glutmain(argc, argv, 640,480,"Bullet Physics Demo. http://bulletphysics.com",&demoApp);
    }
}
