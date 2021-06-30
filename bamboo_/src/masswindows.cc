#include "massWindow.h"
#include <iostream>
#include <json/json.h>
#include <math.h>
#include <TRandom.h>
// The purpose of this class is to see if a specific point falls inside an
// ellipse or not.
// This is done by converting ellipses to circles. I.e., given
// (x, y) point on the ellipse, get
// (x', y') point on the circle.
// |x'|     |M11  M12|   |x|      x' = M11*x + M12*y
// |  |  =  |        | * | | --> 
// |y'|     |M21  M22|   |y|      y' = M21*x + M22*y
// - Default constructor massWindow(...):    initializes the variables.
// - radius(...):                            computes rho.
// Next three functions: not used anymore
// - getValue(...):                          returns the interpolated value of the transformation matrix in a given point.
// - applyGlobalTransformation(...):         returns the coordinates (x', y').
// - isInEllipse(...):                       returns true if a point is inside the circle (false if outside).


massWindow::massWindow(double xc, double yc, double p00, double p01, double p10, double p11) : m_xc(xc), m_yc(yc), m_p00(p00), m_p01(p01), m_p10(p10), m_p11(p11)
{}

int massWindow::getNumberOfEllipses(std::string filename) {

    int n_ellipse = 0;
    std::ifstream ifile(filename);
    Json::Reader reader;
    Json::Value text;
    if (!ifile) std::cout << "ERROR OPENING FILE" << std::endl;
    if (ifile && reader.parse(ifile, text)) {
        n_ellipse = text.size();
    }
    std::cout << "n_ellipse: " << n_ellipse << std::endl;
    return n_ellipse;
}

double massWindow::radius(double px, double py)
{
    const double dx = px - m_xc;
    const double dy = py - m_yc;
    const double p1 = m_p00*dx + m_p01*dy;
    const double p2 = m_p10*dx + m_p11*dy;
    const double dist = std::sqrt(p1*p1 + p2*p2);
    return ( dist > 3 ? 3.2 : dist ); //This is for the overflow bin. Set a value that falls into the last bin (between 3 and 3.5)
}
