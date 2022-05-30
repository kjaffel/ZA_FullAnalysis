#include "th1fmorph_2param.h"
#include "TROOT.h"
#include "TAxis.h"
#include "TArrayD.h"

#include <stdexcept>
#include <iostream>
#include <cmath>
#include <set>

using namespace std;

template<typename TH1_t, typename Value_t>
TH1_t *th1fmorph_2param_(const char *chname, const char *chtitle,
                 		 TH1_t *hist1,TH1_t *hist2, TH1_t *hist3,
                 		 Double_t* par1, Double_t* par2, Double_t* par3,Double_t* parinterp,
                 		 Double_t morphedhistnorm,
                 		 Int_t idebug)
{
	// Return right away if one of the input histograms doesn't exist.
	if(!hist1) {
		cout << "ERROR! th1morph says first input histogram doesn't exist." << endl;
		return(0);
	}
	if(!hist2) {
		cout << "ERROR! th1morph says second input histogram doesn't exist." << endl;
		return(0);
	}
	if(!hist3) {
		cout << "ERROR! th1morph says third input histogram doesn't exist." << endl;
		return(0);
	}

	// Extract bin parameters of input histograms 1 and 2. 
	// Supports the cases of non-equidistant as well as equidistant binning
	// and also the case that binning of histograms 1 and 2 is different.
	TAxis* axis1 = hist1->GetXaxis();
	Int_t nb1 = axis1->GetNbins();
	TAxis* axis2 = hist2->GetXaxis();
	Int_t nb2 = axis2->GetNbins();
	TAxis* axis3 = hist3->GetXaxis();
	Int_t nb3 = axis3->GetNbins();

	std::set<Double_t> bedgesn_tmp;
	for(Int_t i = 1; i <= nb1; ++i){
		bedgesn_tmp.insert(axis1->GetBinLowEdge(i));
		bedgesn_tmp.insert(axis1->GetBinUpEdge(i));
	}
	for(Int_t i = 1; i <= nb2; ++i){
		bedgesn_tmp.insert(axis2->GetBinLowEdge(i));
		bedgesn_tmp.insert(axis2->GetBinUpEdge(i));
	}
	for(Int_t i = 1; i <= nb3; ++i){
		bedgesn_tmp.insert(axis3->GetBinLowEdge(i));
		bedgesn_tmp.insert(axis3->GetBinUpEdge(i));
	}
	Int_t nbn = bedgesn_tmp.size() - 1;
	TArrayD bedgesn(nbn+1);
	Int_t idx = 0;
	for (std::set<Double_t>::const_iterator bedge = bedgesn_tmp.begin();
			bedge != bedgesn_tmp.end(); ++bedge){
		bedgesn[idx]=(*bedge);
		++idx;
	}
	Double_t xminn = bedgesn[0];
	Double_t xmaxn = bedgesn[nbn];


	Double_t wt1,wt2,wt3;

	if (par1[0] == par2[0] && par2[0] == par3[0]){
		 	
	}
	else if (par1[1] == par2[1] && par2[1] == par3[1]){
		
	}
	else{
		wt1 = ((par2[1]-par3[1])*(parinterp[0]-par3[0]) + (par3[0]-par2[0])*(parinterp[1]-par3[1])) / ((par2[1]-par3[1])*(par1[0]-par3[0]) + (par3[0]-par2[0])*(par1[1]-par3[1])) ;
		wt2 = ((par3[1]-par1[1])*(parinterp[0]-par3[0]) + (par1[0]-par3[0])*(parinterp[1]-par3[1])) / ((par2[1]-par3[1])*(par1[0]-par3[0]) + (par3[0]-par2[0])*(par1[1]-par3[1])) ;
		wt3 = 1 - wt1 - wt2;
	}

	//......Give a warning if this is an extrapolation.

	if (wt1 < 0. || wt1 > 1. || wt2 < 0. || wt2 > 1. || wt3 < 0. || wt3 > 1.){
		cout << "Warning! th1fmorph_2param: This is an extrapolation!! Weights are "
			<< wt1 << " and " << wt2 << " and "<< wt3 << std::endl;
		throw std::invalid_argument("Extrapolation");
	}
	if (idebug >= 1) cout << "th1morph - Weights: " << wt1 << " " << wt2 << " " << wt3 << endl;

	if (idebug >= 1) cout << "New hist: bins " << nbn << " from " << xminn << " to " << xmaxn << endl;

	// Treatment for empty histograms: Return an empty histogram
	// with interpolated bins.

	if (hist1->GetSum() <= 0 || hist2->GetSum() <=0 || hist3->GetSum() <=0) {
		cout << "Warning! th1morph detects an empty input histogram. Empty interpolated histogram returned: " 
			<<endl << "         " << chname << " - " << chtitle << endl;
		TH1_t *morphedhist = (TH1_t *)gROOT->FindObject(chname);
		if (morphedhist) delete morphedhist;
		morphedhist = new TH1_t(chname,chtitle,nbn,xminn,xmaxn);
		return(morphedhist);
	}
	if (idebug >= 1) cout << "Input histogram content sums: " 
		<< hist1->GetSum() << " " << hist2->GetSum() << " " << hist3->GetSum() << endl;
	// *         
	// *......Extract the single precision histograms into double precision arrays

	Value_t *dist1=hist1->GetArray(); 
	Value_t *dist2=hist2->GetArray();
	Value_t *dist3=hist3->GetArray();
	Double_t *sigdis1 = new Double_t[1+nb1];
	Double_t *sigdis2 = new Double_t[1+nb2];
	Double_t *sigdis3 = new Double_t[1+nb3];
	Double_t *sigdisn = new Double_t[3+nb1+nb2+nb3];
	Double_t *xdisn   = new Double_t[3+nb1+nb2+nb3];
	Double_t *sigdisf = new Double_t[nbn+1];

	for(Int_t i=0;i<3+nb1+nb2+nb3;i++) xdisn[i] = 0; // Start with empty edges
	sigdis1[0] = 0; sigdis2[0] = 0; sigdis3[0] = 0;// Start with cdf=0 at left edge

	for(Int_t i=1;i<nb1+1;i++) {   // Remember, bin i has edges at i-1 and 
		sigdis1[i] = dist1[i];       // i and i runs from 1 to nb.
	}
	for(Int_t i=1;i<nb2+1;i++) {
		sigdis2[i] = dist2[i];
	}
	for(Int_t i=1;i<nb3+1;i++) {
		sigdis3[i] = dist3[i];
	}

	if (idebug >= 3) {
		for(Int_t i=0;i<nb1+1;i++) {
			cout << i << " dist1 " << dist1[i] << endl;
		}
		for(Int_t i=0;i<nb2+1;i++) {
			cout << i << " dist2 " << dist2[i] << endl;
		}
		for(Int_t i=0;i<nb3+1;i++) {
			cout << i << " dist3 " << dist3[i] << endl;
		}
	}

	//......Normalize the distributions to 1 to obtain pdf's and integrate 
	//      (sum) to obtain cdf's.

	Double_t total = 0,norm1, norm2, norm3;
	for(Int_t i=0;i<nb1+1;i++) {
		total += sigdis1[i];
	}
	if (idebug >=1) cout << "Total histogram 1: " <<  total << endl;
	for(Int_t i=1;i<nb1+1;i++) {
		sigdis1[i] = sigdis1[i]/total + sigdis1[i-1];
	}
	norm1 = total;

	total = 0.;
	for(Int_t i=0;i<nb2+1;i++) {
		total += sigdis2[i];
	}
	if (idebug >=1) cout << "Total histogram 2: " <<  total << endl;
	for(Int_t i=1;i<nb2+1;i++) {
		sigdis2[i] = sigdis2[i]/total + sigdis2[i-1];
	}
	norm2 = total;  

	total = 0.;
	for(Int_t i=0;i<nb3+1;i++) {
		total += sigdis3[i];
	}
	if (idebug >=1) cout << "Total histogram 3: " <<  total << endl;
	for(Int_t i=1;i<nb3+1;i++) {
		sigdis3[i] = sigdis3[i]/total + sigdis3[i-1];
	}
	norm3 = total;  


	// *
	// *......We are going to step through all the edges of both input
	// *      cdf's ordered by increasing value of y. We start at the
	// *      lower edge, but first we should identify the upper ends of the
	// *      curves. These (ixl1, ixl2) are the first point in each cdf from 
	// *      above that has the same integral as the last edge.
	// *

	Int_t ix1l = nb1;
	Int_t ix2l = nb2;
	Int_t ix3l = nb3;
	while(sigdis1[ix1l-1] >= sigdis1[ix1l]) {
		ix1l = ix1l - 1;
	}
	while(sigdis2[ix2l-1] >= sigdis2[ix2l]) {
		ix2l = ix2l - 1;
	}
	while(sigdis3[ix3l-1] >= sigdis3[ix3l]) {
		ix3l = ix3l - 1;
	}

	// *
	// *......Step up to the beginnings of the curves. These (ix1, ix2) are the
	// *      first non-zero points from below.

	Int_t ix1 = -1;
	do {
		ix1 = ix1 + 1;
	} while(sigdis1[ix1+1] <= sigdis1[0]);

	Int_t ix2 = -1;
	do {
		ix2 = ix2 + 1;
	} while(sigdis2[ix2+1] <= sigdis2[0]);

	Int_t ix3 = -1;
	do {
		ix3 = ix3 + 1;
	} while(sigdis3[ix3+1] <= sigdis3[0]);

	if (idebug >= 1) {
		cout << "First and last edge of hist1: " << ix1 << " " << ix1l << endl;
		cout << "   " << sigdis1[ix1] << " " << sigdis1[ix1+1] << endl;
		cout << "First and last edge of hist2: " << ix2 << " " << ix2l << endl;
		cout << "   " << sigdis2[ix2] << " " << sigdis2[ix2+1] << endl;
		cout << "First and last edge of hist3: " << ix3 << " " << ix3l << endl;
		cout << "   " << sigdis3[ix3] << " " << sigdis3[ix3+1] << endl;
	}

	//......The first interpolated point should be computed now.

	Int_t nx4 = 0;
	Double_t x1,x2,x3,x;
	x1 = axis1->GetBinLowEdge(ix1+1); 
	x2 = axis2->GetBinLowEdge(ix2+1); 
	x3 = axis3->GetBinLowEdge(ix3+1); 
	x = wt1*x1 + wt2*x2 + wt3*x3;
	xdisn[nx4] = x;
	sigdisn[nx4] = 0;
	if(idebug >= 1) {
		cout << "First interpolated point: " << xdisn[nx4] << " " 
			<< sigdisn[nx4] << endl;
	}
 
   
	//......Loop over the remaining point in both curves. Getting the last
	//      points may be a bit tricky due to limited floating point 
	//      precision.

	if (idebug >= 1) {
		cout << "----BEFORE while with ix1=" << ix1 << ", ix1l=" << ix1l 
			<< ", ix2=" << ix2 << ", ix2l=" << ix2l 
			<< ", ix3=" << ix3 << ", ix3l=" << ix3l << endl;
	}

	Double_t yprev = -1; // The probability y of the previous point, it will 
	//get updated and used in the loop.
	Double_t y = 0;
	while((ix1 < ix1l) | (ix2 < ix2l) | (ix3 < ix3l)) {
		if (idebug >= 1 ) cout << "----Top of while with ix1=" << ix1 
			    << ", ix1l=" << ix1l << ", ix2=" << ix2 
				<< ", ix2l=" << ix2l << ", ix3=" << ix3
				<< ", ix3l=" << ix3l << endl;

		//......Increment to the next lowest point. Step up to the next
		//      kink in case there are several empty (flat in the integral)
		//      bins.

		Int_t itype = -1; // Tells which input distribution we need to 
		// see next point of.
		if (((sigdis1[ix1+1] <= sigdis2[ix2+1] && sigdis1[ix1+1] <= sigdis3[ix3+1])|| (ix2 == ix2l && ix3 == ix3l)) && ix1 < ix1l) {
			ix1 = ix1 + 1;
			while(sigdis1[ix1+1] <= sigdis1[ix1] && ix1 < ix1l) {
				ix1 = ix1 + 1;
			}
			itype = 1;
		} 
		else if (((sigdis2[ix2+1] <= sigdis1[ix1+1] && sigdis2[ix2+1] <= sigdis3[ix3+1])|| (ix1 == ix1l && ix3 == ix3l)) && ix2 < ix2l) {
			ix2 = ix2 + 1;
			while(sigdis2[ix2+1] <= sigdis2[ix2] && ix2 < ix2l) {
				ix2 = ix2 + 1;
			}
			itype = 2;
		} 
		else if (ix3 < ix3l) {
			ix3 = ix3 + 1;
			while(sigdis3[ix3+1] <= sigdis3[ix3] && ix3 < ix3l) {
				ix3 = ix3 + 1;
			}
			itype = 3;
		}
		else{
			break;
		}


	if (itype == 1) {
		x1 = axis1->GetBinLowEdge(ix1+1);
		y = sigdis1[ix1];
		Double_t x20 = axis2->GetBinLowEdge(ix2+1);
		Double_t x21 = axis2->GetBinUpEdge(ix2+1);
		Double_t y20 = sigdis2[ix2];
		Double_t y21 = sigdis2[ix2+1];
		Double_t x30 = axis3->GetBinLowEdge(ix3+1);
		Double_t x31 = axis3->GetBinUpEdge(ix3+1);
		Double_t y30 = sigdis3[ix3];
		Double_t y31 = sigdis3[ix3+1];

		//......Calculate where the cummulative probability y in distribution 1
		//      intersects between the 2 points from distribution 2 and 3 which 
		//      bracket it.

		if (y21 > y20) {
			x2 = x20 + (x21-x20)*(y-y20)/(y21-y20);
		} 
		else {
			x2 = x20;
		}
		if (y31 > y30) {
			x3 = x30 + (x31-x30)*(y-y30)/(y31-y30);
		} 
		else {
			x3 = x30;
		}
		if (idebug >= 3) {
			cout << "Triplet for itype=1: x1 = " << sigdis1[ix1]  << "\n"
				<< " x2 in [" << x20 << "," << x21 << "] -> " << x2 << " y2 in [" << sigdis2[ix2] << "," << sigdis2[ix2+1] << "]" << "\n"
				<< " x3 in [" << x30 << "," << x31 << "] -> " << x3 << " y3 in [" << sigdis3[ix3] << "," << sigdis3[ix3+1] << "]" << std::endl;
		}

	} 
	if (itype == 2) {
		x2 = axis2->GetBinLowEdge(ix2+1);
		y = sigdis2[ix2];
		Double_t x10 = axis1->GetBinLowEdge(ix1+1);
		Double_t x11 = axis1->GetBinUpEdge(ix1+1);
		Double_t y10 = sigdis1[ix1];
		Double_t y11 = sigdis1[ix1+1];
		Double_t x30 = axis3->GetBinLowEdge(ix3+1);
		Double_t x31 = axis3->GetBinUpEdge(ix3+1);
		Double_t y30 = sigdis3[ix3];
		Double_t y31 = sigdis3[ix3+1];

		//......Calculate where the cummulative probability y in distribution 2
		//      intersects between the 2 points from distribution 1 and 3 which 
		//      brackets it.

		if (y11 > y10) {
			x1 = x10 + (x11-x10)*(y-y10)/(y11-y10);
		} else {
			x1 = x10;
		}
		if (y31 > y30) {
			x3 = x30 + (x31-x30)*(y-y30)/(y31-y30);
		} 
		else {
			x3 = x30;
		}
		if (idebug >= 3) {
			cout << "Triplet for itype=2: x2 = " << sigdis2[ix2]  << "\n"
				<< " x1 in [" << x10 << "," << x11 << "] -> " << x1 << " y1 in [" << sigdis1[ix1] << "," << sigdis1[ix1+1] << "]" << "\n"
				<< " x3 in [" << x30 << "," << x31 << "] -> " << x3 << " y3 in [" << sigdis3[ix3] << "," << sigdis3[ix3+1] << "]" << std::endl;
		}
	}
	if (itype == 3) {
		x3 = axis3->GetBinLowEdge(ix3+1);
		y = sigdis3[ix3];
		Double_t x10 = axis1->GetBinLowEdge(ix1+1);
		Double_t x11 = axis1->GetBinUpEdge(ix1+1);
		Double_t y10 = sigdis1[ix1];
		Double_t y11 = sigdis1[ix1+1];
		Double_t x20 = axis2->GetBinLowEdge(ix2+1);
		Double_t x21 = axis2->GetBinUpEdge(ix2+1);
		Double_t y20 = sigdis2[ix2];
		Double_t y21 = sigdis2[ix2+1];

		//......Calculate where the cummulative probability y in distribution 2
		//      intersects between the 2 points from distribution 1 and 3 which 
		//      brackets it.

		if (y11 > y10) {
			x1 = x10 + (x11-x10)*(y-y10)/(y11-y10);
		} else {
			x1 = x10;
		}
		if (y21 > y20) {
			x2 = x20 + (x21-x20)*(y-y20)/(y21-y20);
		} 
		else {
			x2 = x20;
		}
		if (idebug >= 3) {
			cout << "Triplet for itype=3: x3 = " << sigdis3[ix3]  << "\n"
				<< " x1 in [" << x10 << "," << x11 << "] -> " << x1 << " y1 in [" << sigdis1[ix1] << "," << sigdis1[ix1+1] << "]" << "\n"
				<< " x2 in [" << x20 << "," << x21 << "] -> " << x2 << " y2 in [" << sigdis2[ix2] << "," << sigdis2[ix2+1] << "]" << std::endl;
		}
	}

 // 	cout << "x1: " << x1 << endl;
	// cout << "x2: " << x2 << endl; 
 //    cout << "x3: " << x3 << endl; 

	//......Interpolate between the x's in the 2 distributions at the 
	//      cummulative probability y. Store the (x,y) for provisional 
	//      edge nx3 in (xdisn[nx3],sigdisn[nx3]). nx3 grows for each point
	//      we add the the arrays. Note: Should probably turn the pair into 
	//      a structure to make the code more object-oriented and readable.
	if (idebug >= 1) {
		cout << "y = " << y << "  yprev = " << yprev << std::endl; 
	}

	x = wt1*x1 + wt2*x2 + wt3*x3;

	//cout << "x: " << x << endl;

	if (y > yprev) {
		nx4 = nx4+1;
		if (idebug >= 1) {
			cout << " ---> y > yprev: itype=" << itype << ", nx4=" 
				<< nx4 << ", x= " << x << ", y=" << y << ", yprev=" << yprev 
				<< endl;
		}
		yprev = y;
		xdisn[nx4] = x;
		sigdisn[nx4] = y;
		if(idebug >= 1) {
			cout << "    ix1=" << ix1 << ", ix2= " << ix2 << ", ix3= " << ix3 << ", itype= " << itype 
				<< ", sigdis1[ix1]=" << sigdis1[ix1] 
				<< ", sigdis2[ix2]=" << sigdis2[ix2] 
				<< ", sigdis3[ix3]=" << sigdis3[ix3] << endl;
			cout << "        " << ", nx4=" << nx4 << ", x=" << x << ", y= " 
				<< sigdisn[nx4] << endl;
		}
	}
	}
	if (idebug >=3) for (Int_t i=0;i<nx4;i++) {
		cout << " nx " << i << " " << xdisn[i] << " " << sigdisn[i] << endl;
	}

	// *......Now we loop over the edges of the bins of the interpolated
	// *      histogram and find out where the interpolated cdf 3
	// *      crosses them. This projection defines the result and will
	// *      be stored (after differention and renormalization) in the
	// *      output histogram.
	// *
	// *......We set all the bins following the final edge to the value
	// *      of the final edge.

	x = xmaxn;
	Int_t ix = nbn;

	if (idebug >= 1) cout << "------> Any final bins to set? " << x << " " 
		<< xdisn[nx4] << endl;
	while(x >= xdisn[nx4]) {
		sigdisf[ix] = sigdisn[nx4];
		if (idebug >= 2) cout << "   Setting final bins " << ix << " " << x 
			<< " " << sigdisf[ix] << endl;
		ix = ix-1;
		x = bedgesn[ix];
	}
	Int_t ixl = ix + 1;
	if (idebug >= 1) cout << " Now ixl=" << ixl << " ix=" << ix << endl;

	// *
	// *......The beginning may be empty, so we have to step up to the first
	// *      edge where the result is nonzero. We zero the bins which have
	// *      and upper (!) edge which is below the first point of the
	// *      cummulative distribution we are going to project to this
	// *      output histogram binning.
	// *

	ix = 0;
	x = bedgesn[ix+1];
	if (idebug >= 1) cout << "Start setting initial bins at x=" << x << endl;
	while(x <= xdisn[0]) {
		sigdisf[ix] = sigdisn[0];
		if (idebug >= 1) cout << "   Setting initial bins " << ix << " " << x 
			<< " " << xdisn[1] << " " << sigdisf[ix] << endl;
		ix = ix+1;
		x = bedgesn[ix+1];
	}
	Int_t ixf = ix;

	if (idebug >= 1)
		cout << "Bins left to loop over:" << ixf << "-" << ixl << endl;

	// *......Also the end (from y to 1.0) often comes before the last edge
	// *      so we have to set the following to 1.0 as well.

	Int_t ix4 = 0; // Problems with initial edge!!!
	for(ix=ixf;ix<ixl;ix++) {
		x = bedgesn[ix];
		if (x < xdisn[0]) {
			y = 0;
		} else if (x > xdisn[nx4]) {
			y = 1.;
		} else {
			while(xdisn[ix4+1] <= x && ix4 < 2*nbn) {
				ix4 = ix4 + 1;
			}
			Double_t dx2=axis2->GetBinWidth(axis2->FindBin(x));
			if (xdisn[ix4+1]-x > 1.1*dx2) { // Empty bin treatment
				y = sigdisn[ix4+1];
			}
			else if (xdisn[ix4+1] > xdisn[ix4]) { // Normal bins
				y = sigdisn[ix4] + (sigdisn[ix4+1]-sigdisn[ix4])
					*(x-xdisn[ix4])/(xdisn[ix4+1]-xdisn[ix4]);
			} else {  // Is this ever used?
				y = 0;
				cout << "Warning - th1fmorph_2param: This probably shoudn't happen! " 
					<< endl;
				cout << "Warning - th1fmorph_2param: Zero slope solving x(y)" << endl;
			}
		}
		sigdisf[ix] = y;
		if (idebug >= 3) {
			cout << ix << ", ix4=" << ix4 << ", xdisn=" << xdisn[ix4] << ", x=" 
				<< x << ", next xdisn=" << xdisn[ix4+1] << endl;
			cout << "   cdf n=" << sigdisn[ix4] << ", y=" << y << ", next point=" 
				<< sigdisn[ix4+1] << endl;
		}

	}

	//......Differentiate interpolated cdf and return renormalized result in 
	//      new histogram. 

	TH1_t *morphedhist = (TH1_t *)gROOT->FindObject(chname);
	if (morphedhist) delete morphedhist;
	morphedhist = new TH1_t(chname,chtitle,nbn,bedgesn.GetArray());

	Double_t norm = morphedhistnorm;
	// norm1, norm2, wt1, wt2 are computed before the interpolation
	if (norm <= 0) {
		if (norm1 == norm2 && norm1 == norm3) {
			norm = norm1;
		} else {
			norm   = wt1*norm1 + wt2*norm2 + wt3*norm3;
		}
	}

	for(ix=nbn-1;ix>-1;ix--) {
		y = sigdisf[ix+1]-sigdisf[ix];
		morphedhist->SetBinContent(ix+1,y*norm);
		cout << "y: " << y*norm << endl;
	}

	//......Clean up the temporary arrays we allocated.

	delete [] sigdis1; delete [] sigdis2; delete [] sigdis3;
	delete [] sigdisn; delete [] xdisn; delete [] sigdisf;

	//......All done, return the result.

	return(morphedhist);
}


TH1F *th1fmorph_2param(const char *chname, 
		const char *chtitle,
		TH1F *hist1,TH1F *hist2, TH1F *hist3,
		Double_t* par1, Double_t* par2, Double_t* par3,Double_t* parinterp,
		Double_t morphedhistnorm,
		Int_t idebug)
{ return th1fmorph_2param_<TH1F, Float_t>(chname, chtitle, hist1, hist2, hist3, par1, par2, par3, parinterp, morphedhistnorm, idebug); }

TH1D *th1fmorph_2param(const char *chname, 
		const char *chtitle,
		TH1D *hist1,TH1D *hist2, TH1D *hist3,
		Double_t* par1, Double_t* par2, Double_t* par3,Double_t* parinterp,
		Double_t morphedhistnorm,
		Int_t idebug)
{ return th1fmorph_2param_<TH1D, Double_t>(chname, chtitle, hist1, hist2, hist3, par1, par2, par3, parinterp, morphedhistnorm, idebug); }

