'''===================================================================
Copyright 2019 Matthias Komm, Vilius Cepaitis, Robert Bainbridge, 
Alex Tapper, Oliver Buchmueller. All Rights Reserved. 
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
    
Unless required by applicable law or agreed to in writing, 
software distributed under the License is distributed on an "AS IS" 
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express 
or implied.See the License for the specific language governing 
permissions and limitations under the License.
==================================================================='''


import ROOT

ROOT.gROOT.SetStyle("Plain")
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetOptDate(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFile(0)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetTitleColor(1, "XYZ")
ROOT.gStyle.SetTitleFont(43, "XYZ")
ROOT.gStyle.SetTitleSize(30, "XYZ")
ROOT.gStyle.SetTitleXOffset(1.8)
ROOT.gStyle.SetTitleOffset(1.6, "YZ")

ROOT.gStyle.SetLabelColor(1, "XYZ")
ROOT.gStyle.SetLabelFont(43, "XYZ")
ROOT.gStyle.SetLabelSize(26, "XYZ")

ROOT.gStyle.SetAxisColor(1, "XYZ")
ROOT.gStyle.SetAxisColor(1, "XYZ")
ROOT.gStyle.SetStripDecimals(True)
ROOT.gStyle.SetNdivisions(1005, "X")
ROOT.gStyle.SetNdivisions(506, "Y")

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)

ROOT.gStyle.SetPaperSize(8.0*1.35,6.7*1.35)
ROOT.TGaxis.SetMaxDigits(3)
ROOT.gStyle.SetLineScalePS(2)

def make_plot(pt_hists,ctau_hists):
    class_names = ['b jet','c jet','uds jet','g jet','LLP jet']
    colors = [ROOT.kAzure-4,ROOT.kOrange+7,ROOT.kViolet+1,ROOT.kGreen+1,ROOT.kGray]

    cv = ROOT.TCanvas("cv","",800,750)
    cv.Divide(1,2,0,0)
    cv.GetPad(1).SetPad(0,0.5,1,1)
    cv.GetPad(1).SetMargin(0.14,0.2,0.2,0.04)
    cv.GetPad(2).SetPad(0,0.0,1,0.5)
    cv.GetPad(2).SetMargin(0.14,0.2,0.2,0.04)
    
    cv.cd(1)
    axis_pt = ROOT.TH2F("axis_pt",";log#lower[0.2]{#scale[0.8]{10}} (p#lower[0.2]{#scale[0.8]{T}} / 1 GeV);Resampled jets",50,1.3,3.0,50,0,1.1*max(map(lambda h: h.GetMaximum(),pt_hists)))
    axis_pt.GetXaxis().SetTickSize(0.05)
    axis_pt.GetYaxis().SetTickSize(0.02)
    axis_pt.Draw("AXIS")
    
    legend = ROOT.TLegend(0.81,0.96,0.99,0.2)
    legend.SetBorderSize(0)
    legend.SetTextFont(43)
    legend.SetTextSize(30)
    legend.SetFillStyle(0)
    
    for i,hist in enumerate(pt_hists):
        hist.SetLineColor(colors[i])
        hist.SetLineWidth(2)
        hist.Draw("Same")
        legend.AddEntry(hist,class_names[i],"L")
        
    cv.GetPad(1).RedrawAxis()
    legend.Draw("Same")
    
        
    cv.cd(2)
    axis_ctau = ROOT.TH2F("axis_ctau",";log#lower[0.2]{#scale[0.8]{10}} (c#tau / 1 mm);Resampled jets",50,-2.,5.,50,0,1.1*max(map(lambda h: h.GetMaximum(),ctau_hists)))
    axis_ctau.GetXaxis().SetTickSize(0.05)
    axis_ctau.GetYaxis().SetTickSize(0.02)
    axis_ctau.Draw("AXIS")
    for i,hist in enumerate(ctau_hists):
        hist.SetLineColor(colors[i])
        hist.SetLineWidth(2)
        hist.Draw("Same")
        
    cv.GetPad(2).RedrawAxis()
    
    
    
        
    cv.Print("pipeline.pdf")
