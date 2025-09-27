import React from 'react';
import { FaBook, FaDownload, FaGithub, FaShoppingCart, FaTelegram } from 'react-icons/fa';
import { LuCloudLightning, LuServer, LuStore, LuWrench } from 'react-icons/lu';
import Layout from "@theme/Layout";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Link from '@docusaurus/Link';

const FeatureBox = ({ icon, title, description }) => (
    <div className="bg-gray-700 p-6 rounded-lg shadow-md">
        <div className="primary mb-4">{icon}</div>
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

            <main className="container mx-auto px-4 py-12 flex flex-col justify-center items-center">
                <section className="mb-16">
                    <img
                        src="/img/raspiblitz.jpg"
                        alt="Raspberry Pi Blitz"
                        className="w-full max-w-2xl mx-auto rounded-lg shadow-lg mb-8 border-2 border-black"
                        style={{ borderWidth: '1px', borderColor: '#000', borderStyle: 'solid' }}
                    />
                    <p className="text-center text-white max-w-2xl mx-auto">
                        RaspiBlitz is an open-source project that allows you to run your own Bitcoin and Lightning
                        Network node on a Raspberry Pi.
                    </p>
                </section>

                <section className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
                    <FeatureBox
                        icon={<FaDownload size={24} />}
                        title="Easy Installation"
                        description="Download pre-built SD card images for quick and easy setup on your Raspberry Pi."
                    />
                    <FeatureBox
                        icon={<LuServer size={24} />}
                        title="Full Bitcoin Node"
                        description="Operate a full Bitcoin node to verify the blockchain and transactions yourself."
                    />
                    <FeatureBox
                        icon={<LuCloudLightning size={24} />}
                        title="Lightning Network"
                        description="Run a Lightning Node to send and receive fast, low-cost Bitcoin transactions."
                    />
                    <FeatureBox
                        icon={<LuStore size={24} />}
                        title="Additional Apps"
                        description="Install and access additional apps and services directly from RaspiBlitz node."
                    />
                    <FeatureBox
                        icon={<FaGithub size={24} />}
                        title="Open Source"
                        description="All parts of RaspiBlitz are MIT licensed, and thus fully open source."
                    />
                    <FeatureBox
                        icon={<LuWrench size={24} />}
                        title="Buy RaspiBlitz pre-built or Build yourself"
                        description="You can build RaspiBlitz yourself or buy a pre-built RaspiBlitz from a third party."
                    />
                </section>

                <section className="mb-16">
                    <h2 className="text-3xl font-semibold mb-6 text-center">Get Started</h2>
                    <div className="grid md:grid-cols-3 gap-8">
                        <div className="bg-gray-700 p-6 rounded-lg shadow-md">
                            <h3 className="text-xl font-semibold mb-4">Download</h3>
                            <p className="mb-4">Get the latest version for installation and updates:</p>
                            <Link
                                href="/docs/setup/software-setup/download"
                                className="primary flex items-center"
                            >
                                <FaDownload className="mr-2" /> RaspberryPi SD-Card Images
                            </Link>
                        </div>
                        <div className="bg-gray-700 p-6 rounded-lg shadow-md">
                            <h3 className="text-xl font-semibold mb-4">Documentation</h3>
                            <p className="mb-4">Learn how to build and set up your RaspiBlitz:</p>
                            <Link
                                href="/docs/setup/intro"
                                className="primary flex items-center"
                            >
                                <FaBook className="mr-2" /> RaspiBlitz Documentation
                            </Link>
                        </div>
                        <div className="bg-gray-700 p-6 rounded-lg shadow-md">
                            <h3 className="text-xl font-semibold mb-4">Buy</h3>
                            <p className="mb-4">Find shops to buy a pre-built RaspiBlitz</p>
                            <Link
                                href="/docs/shops"
                                className="primary flex items-center"
                            >
                                <FaShoppingCart className="mr-2" /> Find Shops
                            </Link>
                        </div>
                    </div>
                </section>

                <section className="flex justify-around md:flex-row flex-col gap-8">
                    <section className="mb-16 w-full md:w-1/2 text-white">
                        <h2 className="text-3xl font-semibold mb-6 text-center text-white">Donate to RaspiBlitz</h2>
                        <h4 className='mb-6 text-center'>If you would like to support the project, you can donate with the QR code below, use our lightning address or follow the link to pay with lightning or on-chain via BTCPay</h4>
                        <div className="bg-gray-700 p-6 rounded-lg shadow-md text-center flex flex-col">
                            <img
                                src="/img/qr_donate.png"
                                alt="Donate to RaspiBlitz Project with Lightning Address"
                                className="w-32 h-32 mx-auto mb-4"
                            />
                            <Link href='https://docs.raspiblitz.org/donation.html' className="primary underline">Donate with BTCPay</Link>
                            <p className="mb-2">Lightning Address: <span className='primary'>raspiblitz@btcpay.fulmo.org</span></p>
                            <p className="text-sm">
                                All donations for the RaspiBlitz project are collected by{" "}
                                <Link href="https://fulmo.org" target="_blank" rel="noreferrer"
                                    className="primary">
                                    Fulmo
                                </Link>{" "}
                                & managed together with the developer team.
                            </p>
                        </div>
                    </section>

                    <section className="mb-16 w-full md:w-1/2">
                        <h2 className="text-3xl font-semibold mb-6 text-center">Community and Support</h2>
                        <h4 className='mb-6 text-center'>If you have questions or need support, you can join one of the community-driven telegram groups or open a issue / discussion on GitHub</h4>
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {[
                                { name: "English", link: "https://t.me/raspiblitz" },
                                { name: "Deutsch", link: "https://t.me/raspiblitz_DE" },
                                { name: "Español", link: "https://t.me/raspiblitz_ES" },
                                { name: "Italiano", link: "https://t.me/raspiblitz_IT" },
                                { name: "Русский", link: "https://t.me/raspiblitz_RU" },
                            ].map((group) => (
                                <Link
                                    key={group.name}
                                    href={group.link}
                                    className="bg-gray-700 p-4 rounded-lg shadow-md flex items-center justify-center primary"
                                >
                                    <FaTelegram className="h-8 w-8 mr-2" /> Telegram Group {group.name}
                                </Link>
                            ))}
                            <Link
                                href="https://github.com/raspiblitz/raspiblitz/issues"
                                className="bg-gray-700 p-4 rounded-lg shadow-md flex items-center justify-center primary"
                            >
                                <FaGithub className="h-8 w-8 mr-2" /> GitHub Issues
                            </Link>
                            <Link
                                href="https://github.com/raspiblitz/raspiblitz/discussions"
                                className="bg-gray-700 p-4 rounded-lg shadow-md flex items-center justify-center primary"
                            >
                                <FaGithub className="h-8 w-8 mr-2" /> GitHub Discussions
                            </Link>
                        </div>
                    </section>
                </section>
            </main>
        </div>
    );
};


export default function Home() {
    const { siteConfig } = useDocusaurusContext();
    return (
        <Layout
            title={`${siteConfig.title} Documentation`}
            description="Raspiblitz is your DIY Bitcoin & Lightning Node on a RaspberryPi"
        >
            <main>
                <RaspiBlitzOverview />
            </main>
        </Layout>
    );
}