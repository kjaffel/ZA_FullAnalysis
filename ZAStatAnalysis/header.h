// orignal author : Florian Bury
template <typename T>
float* getContentFromTH1(const T& h)
{
    int Nx = h.GetNbinsX();
    float* content = new float[3*Nx+1];
        // [0:Nx] -> bin content (len = Nx)
        // [Nx:2*Nx] -> bin error (len = Nx)
        // [2*Nx:3*Nx+1] -> bin edges (len = Nx+1)
    for (int i = 0 ; i < Nx ; i++)
    {
        content[i]        = h.GetBinContent(i+1);
        content[Nx+i]     = h.GetBinError(i+1);
        content[2*Nx+i]   = h.GetBinLowEdge(i+1);
    }
    content[3*Nx] = h.GetBinLowEdge(Nx+1);
    
    return content;
}

template <typename T>
float* getContentFromTH2(const T& h)
{
    int Nx = h.GetNbinsX();
    int Ny = h.GetNbinsY();
    float* content = new float[2*Nx*Ny+Nx+Ny+2];
        // [0:Nx*Ny] -> bin content (len = Nx*Ny) : rows = y values, columns = x values
        // [Nx*Ny:2*Nx*Ny] -> bin error (len = Nx*Ny)
        // [2*Nx*Ny:2*Nx*Ny+Nx+Ny+2] -> bin edges (len = Nx+Ny+2)
    for (int x = 0 ; x < Nx; x++)
    {
        for (int y = 0 ; y < Ny; y++)
        {
            content[y + Ny*x] = h.GetBinContent(x+1,y+1);
            content[Nx*Ny + y + Ny*x] = h.GetBinError(x+1,y+1);
            if (x == 0)
                content[2*Nx*Ny + Nx + 1 + y] = h.GetYaxis()->GetBinLowEdge(y+1);
        }
        if (x == 0)
            content[2*Nx*Ny + Nx + Ny + 1] =  h.GetYaxis()->GetBinLowEdge(Ny+1);
        content[2*Nx*Ny + x] = h.GetXaxis()->GetBinLowEdge(x+1);
    }
    content[2*Nx*Ny + Nx] = h.GetXaxis()->GetBinLowEdge(Nx+1);
    return content;
}


TH1F fillTH1(const float* edges, const float* values, const float * errors, int N, std::string name)
{
    TH1F h = TH1F(name.c_str(),name.c_str(),N,edges);
    for (int i = 0 ; i < N ; i++)
    {
        h.SetBinContent(i+1,values[i]);
        h.SetBinError(i+1,errors[i]);
    }    
    return h;
}
TH1D fillTH1(const double* edges, const double* values, const double * errors, int N, std::string name)
{
    TH1D h = TH1D(name.c_str(),name.c_str(),N,edges);
    for (int i = 0 ; i < N ; i++)
    {
        h.SetBinContent(i+1,values[i]);
        h.SetBinError(i+1,errors[i]);
    }    
    return h;
}


TH2F fillTH2(const float* xedges, const float* yedges, const float* values, const float* errors, int Nx, int Ny, std::string name)
{
    TH2F h = TH2F(name.c_str(),name.c_str(),Nx,xedges,Ny,yedges);
    for (int x = 0 ; x < Nx ; x++)
    {
        for (int y = 0 ; y < Ny ; y++)
        {
            h.SetBinContent(x+1,y+1,values[y+x*Nx]);
            h.SetBinError(x+1,y+1,errors[y+x*Nx]);
        }
    }    
    return h;
}

TH2D fillTH2(const double* xedges, const double* yedges, const double* values, const double* errors, int Nx, int Ny, std::string name)
{
    TH2D h = TH2D(name.c_str(),name.c_str(),Nx,xedges,Ny,yedges);
    for (int x = 0 ; x < Nx ; x++)
    {
        for (int y = 0 ; y < Ny ; y++)
        {
            h.SetBinContent(x+1,y+1,values[y+x*Nx]);
            h.SetBinError(x+1,y+1,errors[y+x*Nx]);
        }
    }    
    return h;
}
