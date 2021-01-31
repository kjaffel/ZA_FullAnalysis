#pragma once
class MassWindow {
public:
    MassWindow(double xc, double yc, double p00, double p01, double p10, double p11)
        : m_xc(xc), m_yc(yc), m_p00(p00), m_p01(p01), m_p10(p10), m_p11(p11) {}
    double radius(double px, double py) const {
        const double dx = px - m_xc;
        const double dy = py - m_yc;
        const double p1 = m_p00*dx + m_p01*dy;
        const double p2 = m_p10*dx + m_p11*dy;
        const double radius2 = (p1*p1 + p2*p2);
        return radius2; 
    }
private:
    double m_xc, m_yc; //center of the ellipse
    double m_p00, m_p01, m_p10, m_p11;
 }; 
