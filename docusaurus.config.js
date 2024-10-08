// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import { themes as prismThemes } from "prism-react-renderer";
import tailwindPlugin from "./plugins/tailwind-config.cjs";

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "RaspiBlitz",
  tagline: "DIY Bitcoin and Lightning Node on a RaspberryPi",
  favicon: "img/favicon.ico",

  // Set the production url of your site here
  url: "https://docs.raspiblitz.org",
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: "/",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: "raspiblitz", // Usually your GitHub org/user name.
  projectName: "raspiblitz-docs", // Usually your repo name.
  deploymentBranch: "gh-pages",
  trailingSlash: false,

  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: "./sidebars.js",
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl: "https://github.com/fusion44/raspiblitz/tree/main/docs",
        },
        theme: {
          customCss: "./src/css/custom.css",
        },
      }),
    ],
  ],

  plugins: [tailwindPlugin],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        defaultMode: "dark", // Set default mode to dark
        disableSwitch: true, // Keep the switch in the navbar
        respectPrefersColorScheme: false, // Ignore user system preferences
      },
      // Replace with your project's social card
      image: "img/docusaurus-social-card.jpg",
      navbar: {
        title: "",
        logo: {
          alt: "RaspiBlitz logo",
          src: "img/RaspiBlitz_Logo_Main_Negative.svg",
        },
        items: [
          {
            type: "docSidebar",
            sidebarId: "blitzSidebar",
            position: "left",
            label: "Documentation",
          },
          {
            href: "https://github.com/raspiblitz/raspiblitz",
            label: "GitHub",
            position: "right",
          },
          {
            href: "https://docs.raspiblitz.org/docs/setup/software-setup/download",
            label: "Download",
            position: "right",
          },
        ],
      },
      footer: {
        style: "dark",
        links: [],
        copyright: `Copyright © ${new Date().getFullYear()} RaspiBlitz open source project. Built with Docusaurus. Impressum: Christian Rotzoll, christian [ at ] rotzoll.de - this site is not using any cookies and is not storing your data. Icons by https://fontawesome.com/ (CC BY 4.0) and https://lucide.dev/ (ISC)`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
      algolia: {
        appId: "H1OPUQUC79",
        apiKey: "5ae665bb7d16f08c07105a628adcd2bc",
        indexName: "raspiblitz",
        contextualSearch: false, // only false works
      },
    }),
};

export default config;
