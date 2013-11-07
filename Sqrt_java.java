/*
 * Copyright (C) 2013 CK Telecom Inc. All rights reserved.
 *
 * @File Sqrt_java.java
 * @Author tao.pei jypeitao@163.com
 * @Data 2013-11-7
 */

public class Sqrt_java {

    //fast inverse square root
    //1/sqrt(x)
    public static float invSqrt(float x) {
        float xhalf = 0.5f*x;
        int i = Float.floatToIntBits(x);
        i = 0x5f3759df - (i>>1);
        //i = 0x5f375a86 - (i>>1);
        x = Float.intBitsToFloat(i);
        x = x*(1.5f - xhalf*x*x);
        return x;
    }
    
    public static double invSqrt(double x) {
        double xhalf = 0.5d*x;
        long i = Double.doubleToLongBits(x);
        i = 0x5fe6ec85e7de30daL - (i>>1);
        //i = 0x5fe6eb50c7aa19f9L - (i>>1);
        x = Double.longBitsToDouble(i);
        x = x*(1.5d - xhalf*x*x);
        return x;
    }
}
