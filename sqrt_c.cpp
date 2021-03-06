
//1/sqrt()
float InvSqrt(float x)
{
	float xhalf = 0.5f*x;
	int i = *(int*)&x; // get bits for floating VALUE
	i = 0x5f375a86- (i>>1); // gives initial guess y0
	//i = 0x5f3759df - (i>>1);
	x = *(float*)&i; // convert bits BACK to float
	x = x*(1.5f-xhalf*x*x); // Newton step, repeating increases accuracy
	return x;
}
