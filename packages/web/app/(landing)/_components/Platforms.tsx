import { RiRobot2Line } from "react-icons/ri";
import { LuClock4 } from "react-icons/lu";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";

export type TPlatform = {
  id: string;
  name: string;
  icon: React.ReactNode;
  available: boolean;
  steps?: string[];
};

export function Platforms({ platforms }: { platforms: TPlatform[] }) {
  const [activeTab, setActiveTab] = useState("telegram");

  return (
    <div className="max-w-4xl mx-auto">
      {/* Tabs */}
      <div className="flex flex-wrap justify-center mb-8 gap-2">
        {platforms.map((platform) => (
          <button
            key={platform.id}
            onClick={() => setActiveTab(platform.id)}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all cursor-pointer ${
              activeTab === platform.id ? "bg-primary text-neutral-900" : "bg-white hover:bg-gray-100"
            }`}
          >
            {platform.icon}
            <span>{platform.name}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        <AnimatePresence mode="wait">
          {platforms.map(
            (platform) =>
              activeTab === platform.id && (
                <motion.div
                  key={platform.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                  className="flex flex-col md:flex-row"
                >
                  <div className="md:w-1/2 p-8">
                    <div className="flex items-center gap-3 mb-6">
                      <div
                        className={`h-12 w-12 rounded-full ${platform.available ? "bg-primary/20" : "bg-gray-100"} flex items-center justify-center`}
                      >
                        {platform.icon}
                      </div>
                      <h3 className="text-2xl font-bold">{platform.name}</h3>
                    </div>

                    {platform.available ? (
                      <div>
                        <h4 className="text-xl font-semibold mb-6 text-primary">How It Works</h4>
                        <div className="space-y-6">
                          {platform.steps?.map((step, index) => (
                            <div key={index} className="flex gap-4">
                              <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary font-semibold flex items-center justify-center text-neutral-900">
                                {index + 1}
                              </div>
                              <div>
                                <p className="text-gray-600">{step}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <div className="inline-block p-6 bg-gray-100 rounded-full mb-6">
                          <LuClock4 className="w-10 h-10 text-gray-400" />
                        </div>
                        <h4 className="text-xl font-semibold mb-3">Coming Soon</h4>
                        <p className="text-gray-600 max-w-md mx-auto">
                          We're working hard to bring {platform.name} integration to ViraLink AI. Stay tuned for
                          updates!
                        </p>
                        <button className="mt-6 bg-white border border-gray-300 hover:border-primary px-5 py-2 rounded-full font-medium text-sm transition-colors">
                          Get notified when available
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="md:w-1/2 bg-gray-50 p-8 flex items-center justify-center">
                    {platform.available ? (
                      <div className="relative max-w-xs">
                        <div className="w-[300px] h-[400px] bg-gray-300 rounded-lg shadow-lg border-4 border-white"></div>
                        <div className="absolute -top-4 -right-4 bg-white p-3 rounded-lg shadow-lg">
                          <div className="flex items-center space-x-2">
                            <RiRobot2Line className="w-5 h-5 text-primary" />
                            <span className="font-medium">AI Powered</span>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="relative">
                        <div className="w-[300px] h-[400px] bg-gray-300 rounded-lg shadow-lg opacity-60 grayscale"></div>
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="bg-white/90 px-6 py-3 rounded-full shadow-lg">
                            <span className="font-semibold text-lg flex items-center">
                              <LuClock4 className="w-5 h-5 mr-2 text-primary" />
                              Coming Soon
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ),
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
