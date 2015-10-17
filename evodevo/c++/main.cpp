#include "NoiseWorld.cpp"
#include "GlutStuff.h"
#include "GLDebugDrawer.h"
#include "btBulletDynamicsCommon.h"

/*
g++ -g -std=gnu++11 -I/home/josh/bullet-2.82-r2704/Demos/OpenGL/ -I/home/josh/bullet-2.82-r2704/src/ ./main.cpp -L/home/josh/bullet-build/Demos/OpenGL/ -L/home/josh/bullet-2.82-r2704/bullet-build/src/BulletDynamics/ -L/home/josh/bullet-2.82-r2704/bullet-build/src/BulletCollision/ -L/home/josh/bullet-2.82-r2704/bullet-build/src/LinearMath/ -L/home/josh/bullet-2.82-r2704/bullet-build/Demos/OpenGL -lefence -lOpenGLSupport -lGL -lGLU -lglut -lBulletDynamics -lBulletCollision -lLinearMath -o ./app
*/


GLDebugDrawer	gDebugDrawer;

int main(int argc, char *argv[])

{
  NoiseWorld demoApp;
  bool graphicsOn (true);
  
  if (graphicsOn)
    {
      demoApp.drawGraphics = true;
    }
  else
    {
      demoApp.drawGraphics = false;
    }
  demoApp.initPhysics();
  demoApp.getDynamicsWorld()->setDebugDrawer(&gDebugDrawer);
  if (graphicsOn) 
    {
      return glutmain(argc, argv, 640,480,"Bullet Physics Demo. http://bulletphysics.com",&demoApp);
    }
  else
    {
      while(demoApp.timeStep <= 500) 
	{
	  demoApp.clientMoveAndDisplay();
	}
      return demoApp.Save_Position(true);
    }    
}
