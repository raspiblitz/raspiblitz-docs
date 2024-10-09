import React from 'react';
import {FaBook, FaDownload, FaGithub, FaTelegram} from 'react-icons/fa';
import {LuCloudLightning, LuServer, LuStore, LuWrench} from 'react-icons/lu';
import Layout from "@theme/Layout";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";

const FeatureBox = ({icon, title, description}) => (
    <div className="bg-gray-700 p-6 rounded-lg shadow-md">
        <div className="text-blue-600 mb-4">{icon}</div>
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-white">{description}</p>
    </div>
);

const RaspiBlitzOverview = () => {
    return (
        <div className="bg-gray-800 min-h-screen">
            <header className="text-white py-16 text-center">
                <h1 className="text-4xl font-bold mb-4">RaspiBlitz</h1>
                <p className="text-xl">Your DIY Bitcoin & Lightning Node on a RaspberryPi</p>
            </header>

            <main className="container mx-auto px-4 py-12">
                <section className="mb-16">
                    <img
                        src="/img/raspiblitz.jpg"
                        alt="Raspberry Pi Blitz"
                        className="w-full max-w-2xl mx-auto rounded-lg shadow-lg mb-8"
                    />
                    <p className="text-center text-white max-w-2xl mx-auto">
                        RaspiBlitz is an open-source project that allows you to run your own Bitcoin and Lightning
                        Network node on a Raspberry Pi.
                    </p>
                </section>

                <section className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
                    <FeatureBox
                        icon={<FaDownload size={24}/>}
                        title="Easy Installation"
                        description="Download pre-built SD card images for quick and easy setup on your Raspberry Pi."
                    />
                    <FeatureBox
                        icon={<LuServer size={24}/>}
                        title="Full Bitcoin Node"
                        description="Operate a full Bitcoin node to verify the blockchain and transactions yourself."
                    />
                    <FeatureBox
                        icon={<LuCloudLightning size={24}/>}
                        title="Lightning Network"
                        description="Run a Lightning Node to send and receive fast, low-cost Bitcoin transactions."
                    />
                    <FeatureBox
                        icon={<LuStore size={24}/>}
                        title="Additional Apps"
                        description="Install and access additional apps and services directly from RaspiBlitz node."
                    />
                    <FeatureBox
                        icon={<FaGithub size={24}/>}
                        title="Open Source"
                        description="All parts of RaspiBlitz are MIT licensed, and thus fully open source."
                    />
                    <FeatureBox
                        icon={<LuWrench size={24}/>}
                        title="Buy RaspiBlitz pre-built or Build yourself"
                        description="You can build RaspiBlitz yourself or buy a pre-built RaspiBlitz from a third party."
                    />
                </section>

                <section className="mb-16">
                    <h2 className="text-3xl font-semibold mb-6 text-center">Get Started</h2>
                    <div className="grid md:grid-cols-2 gap-8">
                        <div className="bg-gray-700 p-6 rounded-lg shadow-md">
                            <h3 className="text-xl font-semibold mb-4">Download</h3>
                            <p className="mb-4">Get the latest version for installation and updates:</p>
                            <a
                                href="https://docs.raspiblitz.org/docs/setup/software-setup/download"
                                className="text-blue-600 hover:text-blue-800 flex items-center"
                            >
                                <FaDownload className="mr-2"/> RaspberryPi SD-Card Images
                            </a>
                        </div>
                        <div className="bg-gray-700 p-6 rounded-lg shadow-md">
                            <h3 className="text-xl font-semibold mb-4">Documentation</h3>
                            <p className="mb-4">Learn how to build and set up your RaspiBlitz:</p>
                            <a
                                href="https://docs.raspiblitz.org/docs/setup/intro"
                                className="text-blue-600 hover:text-blue-800 flex items-center"
                            >
                                <FaBook className="mr-2"/> RaspiBlitz Documentation
                            </a>
                        </div>
                    </div>
                </section>

                <section className="flex justify-around md:flex-row flex-col gap-8">
                    <section className="mb-16 w-full md:w-1/2 text-black">
                        <h2 className="text-3xl font-semibold mb-6 text-center text-white">Support the Project</h2>
                        <div className="bg-white p-6 rounded-lg shadow-md text-center">
                            <h3 className="text-xl font-semibold mb-4">Donate to RaspiBlitz</h3>
                            <img
                                src="/img/qr_donate.png"
                                alt="Donate to RaspiBlitz Project with Lightning Address"
                                className="w-32 h-32 mx-auto mb-4"
                            />
                            <p className="mb-2">Lightning Address: raspiblitz@btcypay.fulmo.org</p>
                            <p className="text-sm text-black">
                                All donations for the RaspiBlitz project are collected by{" "}
                                <a href="https://fulmo.org" target="_blank" rel="noopener noreferrer"
                                   className="text-blue-600 hover:text-blue-800">
                                    Fulmo
                                </a>{" "}
                                & managed together with the developer team.
                            </p>
                        </div>
                    </section>

                    <section className="mb-16 w-full md:w-1/2">
                        <h2 className="text-3xl font-semibold mb-6 text-center">Community</h2>
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {[
                                {name: "English", link: "https://t.me/raspiblitz"},
                                {name: "Deutsch", link: "https://t.me/raspiblitz_DE"},
                                {name: "Español", link: "https://t.me/raspiblitz_ES"},
                                {name: "Italiano", link: "https://t.me/raspiblitz_IT"},
                                {name: "Русский", link: "https://t.me/raspiblitz_RU"},
                            ].map((group) => (
                                <a
                                    key={group.name}
                                    href={group.link}
                                    className="bg-white p-4 rounded-lg shadow-md flex items-center justify-center text-blue-600 hover:text-blue-800"
                                >
                                    <FaTelegram className="h-8 w-8 mr-2"/> Telegram Group {group.name}
                                </a>
                            ))}
                            <a
                                href="https://github.com/raspiblitz/raspiblitz/issues"
                                className="bg-white p-4 rounded-lg shadow-md flex items-center justify-center text-blue-600 hover:text-blue-800"
                            >
                                <FaGithub className="h-8 w-8 mr-2"/> GitHub Issues
                            </a>
                            <a
                                href="https://github.com/raspiblitz/raspiblitz/discussions"
                                className="bg-white p-4 rounded-lg shadow-md flex items-center justify-center text-blue-600 hover:text-blue-800"
                            >
                                <FaGithub className="h-8 w-8 mr-2"/> GitHub Discussions
                            </a>
                        </div>
                    </section>
                </section>
            </main>
        </div>
    );
};


export default function Home() {
    const {siteConfig} = useDocusaurusContext();
    return (
        <Layout
            title={`${siteConfig.title} Documentation`}
            description="Raspiblitz is your DIY Bitcoin & Lightning Node on a RaspberryPi"
        >
            <main>
                <RaspiBlitzOverview/>
            </main>
        </Layout>
    );
}