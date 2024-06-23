import clsx from "clsx";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import HomepageFeatures from "@site/src/components/HomepageFeatures";

import Heading from "@theme/Heading";
import styles from "./index.module.css";

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <div style={{ padding: "20px 20px", fontSize: "85%", color: "lightgreen" }}>
      <h2>RaspiBlitz - DIY Bitcoin &amp; Lightning Node on a RaspberryPi</h2>

      <img
        src="https://github.com/rootzoll/raspiblitz/raw/dev/pictures/raspiblitz.jpg"
        alt="Raspberry Pi Blitz"
        style={{
          width: "100%",
          maxWidth: "520px",
          minHeight: "210px",
          borderWidth: "1px",
          borderColor: "grey",
          borderStyle: "solid",
          marginTop: "10px",
          marginBottom: "6px",
        }}
      />
      <div style={{ paddingTop: "15px" }}>
        The complete tutorial on how to build from single parts &amp; setup:
        <ul style={{ padding: "0px 20px", listStyleType: "disc" }}>
          <li>
            <a href="https://docs.raspiblitz.org/docs/setup/intro">
              docs.raspiblitz.org
            </a>
          </li>
        </ul>
      </div>
      <div>
        Source Code (MIT OpenSource):
        <ul style={{ padding: "0px 20px" }}>
          <li>
            Main:{" "}
            <a href="https://github.com/raspiblitz/raspiblitz">
              github.com/raspiblitz/raspiblitz
            </a>
          </li>
          <li>
            WebUI:{" "}
            <a href="https://github.com/raspiblitz/raspiblitz-web">
              github.com/raspiblitz/raspiblitz-web
            </a>
          </li>
          <li>
            API:{" "}
            <a href="https://github.com/fusion44/blitz_api">
              github.com/fusion44/blitz_api
            </a>
          </li>
          <li>
            Docs:{" "}
            <a href="https://github.com/raspiblitz/raspiblitz-docs">
              github.com/raspiblitz/raspiblitz-docs
            </a>
          </li>
        </ul>
        Questions and Support:
        <ul style={{ padding: "0px 20px" }}>
          <li>
            <a href="https://t.me/raspiblitz">Telegram English</a> (community
            managed)
          </li>
          <li>
            <a href="https://t.me/raspiblitz_DE">Telegram Deutsch</a> (community
            managed)
          </li>
          <li>
            <a href="https://t.me/raspiblitz_ES">Telegram Spanish</a> (community
            managed)
          </li>
          <li>
            <a href="https://t.me/raspiblitz_IT">Telegram Italian</a> (community
            managed)
          </li>
          <li>
            <a href="https://t.me/raspiblitz_RU">Telegram Russian</a> (community
            managed)
          </li>
          <li>
            <a href="https://github.com/rootzoll/raspiblitz/issues?q=is%3Aissue">
              GitHub Issues
            </a>
          </li>
        </ul>
      </div>

      <div style={{ paddingTop: "15px" }}>
        Donations for the RaspiBlitz project are collected by{" "}
        <a href="https://fulmo.org" target="_blank">
          Fulmo
        </a>{" "}
        &amp; managed together with the developer team.
      </div>

      <div style={{ paddingTop: "15px" }}>
        Impressum: Christian Rotzoll, christian [ at ] rotzoll.de - this site is
        not using any cookies and is not storing your data.
      </div>
    </div>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />"
    >
      <main>
        <HomepageHeader />
      </main>
    </Layout>
  );
}
