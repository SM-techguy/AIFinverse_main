import React from "react";
import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";
import { Target, BarChart, TrendingUp, Users, Shield, Lightbulb, Zap, Globe, CheckCircle } from "lucide-react";
import PageWrapper from "@/components/PageWrapper";

export default function About() {
  const [, setLocation] = useLocation();

  return (
    <PageWrapper>
     <div className="min-h-screen bg-gradient-to-br from-slate-950/95 via-blue-800/80 to-slate-700/95 bg-[url('/images/login.png')] bg-cover bg-center bg-fixed bg-blend-light">
      <Navbar />

      <main className="pt-24 px-4 max-w-6xl mx-auto">
        {/* HERO SECTION */}
        <section className="text-center mb-16">
          <div className="inline-flex items-center gap-4 mb-6 -ml-4 md:-ml-8">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500/20 to-blue-500/20 rounded-2xl flex items-center justify-center">
              <Target className="w-10 h-10 text-teal-400" />
            </div>
            <div className="text-left">
              <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                AIF𝗶𝗻𝘃𝗲𝗿𝘀𝗲
              </h1>
              <p className="text-xl text-slate-300 mt-2">
                Brings together AI and the financial markets universe.
              </p>
            </div>
          </div>
        </section>

        {/* WHO WE ARE */}
        <section className="mb-16">
          <div className="flex items-center gap-3 mb-8 -ml-2">
            <Users className="w-8 h-8 text-cyan-400" />
            <h2 className="text-3xl font-bold">Who We Are</h2>
          </div>
          
          <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 border border-slate-700 rounded-2xl p-8">
            <p className="text-lg text-slate-300 mb-6">
              This is a passion project, which started as a need to improve trading outcomes and is meant to evolve continuously, based on a roadmap and user feedback.
            </p>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-cyan-500/20 rounded-full flex items-center justify-center mt-1">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                  </div>
                  <p className="text-slate-300">
                    We have spent years closely following stock markets – as both a trader and a long-term investor.
                  </p>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-cyan-500/20 rounded-full flex items-center justify-center mt-1">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                  </div>
                  <p className="text-slate-300">
                    We have trading / investing experience of 15 years in Indian markets and 5 years in the US markets.
                  </p>
                </div>
              </div>
              
              <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                <h3 className="text-xl font-bold text-cyan-300 mb-3">The Challenge</h3>
                <p className="text-slate-300">
                  Over time, one constraint became impossible to ignore: no matter how experienced you are, you can only actively track a limited number of stocks, while the real opportunity set is massive. The market universe is simply too large.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* OUR OBJECTIVE */}
        <section className="mb-16">
          <div className="flex items-center gap-3 mb-8 -ml-2">
            <Target className="w-8 h-8 text-blue-400" />
            <h2 className="text-3xl font-bold">Our Objective</h2>
          </div>
          
          <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 border border-slate-700 rounded-2xl p-8">
            <p className="text-lg text-slate-300 mb-8">
              Having used fundamental & technical analysis extensively, the objective behind AIFinverse is straightforward:
            </p>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mb-4">
                  <Lightbulb className="w-6 h-6 text-teal-400" />
                </div>
                <h3 className="text-xl font-bold mb-2">Reduce Manual Homework</h3>
                <p className="text-slate-400 text-sm">Automate analysis and monitoring</p>
              </div>
              
              <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mb-4">
                  <BarChart className="w-6 h-6 text-teal-400" />
                </div>
                <h3 className="text-xl font-bold mb-2">Expand Market Universe</h3>
                <p className="text-slate-400 text-sm">Track thousands of stocks simultaneously</p>
              </div>
              
              <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mb-4">
                  <TrendingUp className="w-6 h-6 text-teal-400" />
                </div>
                <h3 className="text-xl font-bold mb-2">Improve Trading Outcomes</h3>
                <p className="text-slate-400 text-sm">Better entries, exits, and timing</p>
              </div>
              
              <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mb-4">
                  <CheckCircle className="w-6 h-6 text-teal-400" />
                </div>
                <h3 className="text-xl font-bold mb-2">Increase Confidence</h3>
                <p className="text-slate-400 text-sm">Data-driven decisions you can trust</p>
              </div>
            </div>
          </div>
        </section>

        {/* WHAT TO EXPECT */}
        <section className="mb-16">
          <div className="flex items-center gap-3 mb-8 -ml-2">
            <BarChart className="w-8 h-8 text-purple-400" />
            <h2 className="text-3xl font-bold">What to Expect</h2>
          </div>
          
          <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 border border-slate-700 rounded-2xl p-8">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <div className="flex items-center gap-3 mb-6 -ml-2">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-xl flex items-center justify-center">
                    <span className="text-2xl">📈</span>
                  </div>
                  <h3 className="text-2xl font-bold">Massive Coverage</h3>
                </div>
                <p className="text-slate-300 mb-4">
                  We track over <span className="font-bold text-cyan-400">700 stocks in India</span> and over <span className="font-bold text-cyan-400">1100 stocks in the US</span>, round the clock.
                </p>
                <p className="text-slate-300">
                  Different strategies, selected by users, would trigger alerts generated by proprietary algorithms. Some days / strategies are more active, while others are not.
                </p>
              </div>
              
              <div>
                <div className="flex items-center gap-3 mb-6 -ml-2">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-xl flex items-center justify-center">
                    <span className="text-2xl">🚀</span>
                  </div>
                  <h3 className="text-2xl font-bold">Market Movements</h3>
                </div>
                <p className="text-slate-300 mb-4">
                  Big moves in markets lead to a high number of alerts such as:
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="text-slate-300">52-week highs and all-time highs in positive markets</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="text-slate-300">Breaking important moving averages in down markets</span>
                  </li>
                </ul>
              </div>
            </div>
            
            <div className="mt-8 pt-8 border-t border-slate-700">
              <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                <div className="flex items-start gap-4 -ml-2">
                  <Lightbulb className="w-8 h-8 text-yellow-400 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-xl font-bold text-yellow-300 mb-2">Actionable Intelligence</h3>
                    <p className="text-slate-300 mb-3">
                      Alerts are meant to narrow focus, not force trades. Our alerts are meant to give you actionable intelligence in one place and evolve into giving high probability buy / sell signals based on 10 years of backtesting.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* BENEFITS GRID - FIXED SYNTAX */}
        <section className="mb-16">
          <div className="grid md:grid-cols-2 gap-8">
            {/* FOR TRADERS */}
            <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 border border-slate-700 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6 -ml-2">
                <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
                  <Users className="w-6 h-6 text-teal-400" />
                </div>
                <h2 className="text-2xl font-bold">What's in It for Traders</h2>
              </div>
              
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-orange-400 rounded-full mt-2"></div>
                  <span className="text-slate-300">Alerts based on specific technical indicators on the fly</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-orange-400 rounded-full mt-2"></div>
                  <span className="text-slate-300">News-driven stock alerts</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-orange-400 rounded-full mt-2"></div>
                  <span className="text-slate-300">Daily insights into what is driving markets</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-orange-400 rounded-full mt-2"></div>
                  <span className="text-slate-300">Designed for active and momentum-oriented traders</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-orange-400 rounded-full mt-2"></div>
                  <span className="text-slate-300">Different strategies to suit varied trader needs</span>
                </li>
              </ul>
            </div>

            {/* FOR INVESTORS */}
            <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 border border-slate-700 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6 -ml-2">
                <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-teal-400" />
                </div>
                <h2 className="text-2xl font-bold">What's in It for Investors</h2>
              </div>
              
              <p className="text-slate-300 mb-6">
                Long-term investing always works over time. However, better accumulation levels improve long-term returns. Our alerts would help fundamental investors to:
              </p>
              
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full mt-2"></div>
                  <span className="text-slate-300">Get better entry points</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full mt-2"></div>
                  <span className="text-slate-300">Accumulate on dips</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full mt-2"></div>
                  <span className="text-slate-300">Book profits at optimal levels</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* WHAT AIFINVERSE IS NOT */}
        <section className="mb-16">
          <div className="flex items-center gap-3 mb-8 -ml-2">
            <Shield className="w-8 h-8 text-red-400" />
            <h2 className="text-3xl font-bold">What AIF𝗶𝗻𝘃𝗲𝗿𝘀𝗲 Is NOT</h2>
          </div>
          
          <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 border border-slate-700 rounded-2xl p-8">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-bold text-red-300 mb-4">Not a...</h3>
                <ul className="space-y-3">
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-red-500/20 rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                    </div>
                    <span className="text-slate-300">Brokerage</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-red-500/20 rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                    </div>
                    <span className="text-slate-300">Trading firm</span>
                  </li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-xl font-bold text-red-300 mb-4">Does not...</h3>
                <ul className="space-y-3">
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-red-500/20 rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                    </div>
                    <span className="text-slate-300">Manage or trade user funds</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-red-500/20 rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                    </div>
                    <span className="text-slate-300">Guarantee returns</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-red-500/20 rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                    </div>
                    <span className="text-slate-300">Issue buy/sell calls and dump positions on users</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* TEAM & EXPECTATIONS */}
        <section className="mb-16">
          <div className="grid md:grid-cols-2 gap-8">
            {/* TEAM */}
            <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 border border-slate-700 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6 -ml-2">
                <Shield className="w-6 h-6 text-fuchsia-400" />
                <h2 className="text-2xl font-bold">Who Is Behind It</h2>
              </div>
              
              <p className="text-slate-300 mb-6">
                Team of passionate people in their domains – stock markets and technology.
              </p>
              
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-cyan-300">Focused on:</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full mt-2"></div>
                    <span className="text-slate-300">Building systems</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full mt-2"></div>
                    <span className="text-slate-300">Delivering a platform that adds value to your trading experience</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full mt-2"></div>
                    <span className="text-slate-300">Using AI meaningfully, not superficially</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* EXPECTATIONS */}
            <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 border border-slate-700 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6 -ml-2">
                <Lightbulb className="w-8 h-8 text-yellow-400" />
                <h2 className="text-2xl font-bold">Expectations from Users</h2>
              </div>
              
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-yellow-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-yellow-400">💬</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-200 mb-1">Genuine Feedback</h3>
                    <p className="text-slate-400 text-sm">Share your honest experiences and suggestions</p>
                  </div>
                </li>
                
                <li className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-yellow-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-yellow-400">🎯</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-200 mb-1">Honest Inputs for Improvement</h3>
                    <p className="text-slate-400 text-sm">Help us refine and enhance the platform</p>
                  </div>
                </li>
                
                <li className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-yellow-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-yellow-400">🤝</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-200 mb-1">Collaborative Learning</h3>
                    <p className="text-slate-400 text-sm">Learn and grow together as a community</p>
                  </div>
                </li>
                
                <li className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-yellow-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-yellow-400">🚀</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-200 mb-1">Mutual Growth Journey</h3>
                    <p className="text-slate-400 text-sm">Helping each other on the trading and investing journey</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </section>
      </main>

     
      {/* ================= FOOTER ================= */}
      <footer className="bg-slate-900 border-t border-slate-800 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-3 text-center">
          <p className="text-sm text-slate-400">
            © 2025 All rights reserved to AIFinverse.{" | "}
            <a href="/privacy-policy" className="text-cyan-400 hover:text-cyan-300 hover:underline ml-1">
              Privacy Policy
            </a>
          </p>
        </div>
      </footer>
    </div>
    </PageWrapper>
  );
}