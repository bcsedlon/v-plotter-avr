#ifndef v_h
#define v_h

#include <math.h>

#define DRIVE_STEP_ANGLE M_PI / 800 //step angle [rad]
#define DRIVE_WHEEL_DIAMETER 9.61 //9.5 //wheel diameter [mm]
#define DRIVE_STEP_MULT 2  //2
#define DRIVE_STEP_DISTANCE (DRIVE_STEP_ANGLE / DRIVE_STEP_MULT) * DRIVE_WHEEL_DIAMETER

class vPlotter{
public:
	unsigned long stepDistance = (unsigned int)(DRIVE_STEP_DISTANCE * 1000); //[um]
	int X_0;
	int Y_0;
	int X_SIZE;
	int Y_SIZE;

	void setSize(unsigned int xBase) {
		//automatic calculated printing area for best resolution
		X_SIZE = int(xBase * 0.4);   //X size of drawing area [mm]
		X_0 = int(xBase * 0.3); //X offset from drive L [mm]
		Y_0 = int(xBase * 0.25); //Y offset from drive L [mm]
		Y_SIZE = int(xBase * 0.25); //Y size of drawing area [mm]
		/*
		if Y_SIZE > Y_BASE:
			Y_SIZE = Y_BASE
        if Y_0 > Y_BASE:
        	print "Error: Y_BASE is lower than optimal printing area offset!"
        	exit
		 */
	}
	void setSize(unsigned int xBase, int x0, int y0) {
		X_SIZE = xBase - 2 * x0;
		X_0 = x0;
		Y_0 = y0;
		Y_SIZE = X_SIZE;
	}

	unsigned long getLl(int x, int y) {

		return sqrt(pow(x + X_0, 2) + pow(y + Y_0, 2));
	}

	unsigned long getRl(int x, int y) {
		return sqrt(pow(X_0 + X_SIZE - x, 2) + pow(Y_0 + y, 2));
	}

	int getX(unsigned long Ll, unsigned long Rl) {
		return ((pow(Rl, 2) -  pow(Ll, 2) - pow(X_SIZE, 2)) - (2 * X_SIZE * X_0 )) / ((-2 * X_SIZE) - (4 * X_0));
	}

	int getY(unsigned long Ll, unsigned long Rl) {
		double l2 = pow(Ll, 2) - pow(getX(Ll, Rl) + X_0, 2);
		if(l2 <= 0)
        	return -1;
		else
			return sqrt(l2) - Y_0;
	}

	unsigned long getLength(unsigned long steps) {
		//TODO: overflow?
		return (stepDistance * steps) / 1000; //[mm]
	}

	bool getDirection(unsigned long l, unsigned long lPos) {
		return (l >= lPos);
	}

	unsigned long getStepsTo(unsigned long l, unsigned long lPos) {
		if(l > lPos)
			return ((l - lPos) * 1000 ) / stepDistance;
		else
			return ((lPos - l) * 1000 ) / stepDistance;
	}
};

#endif
