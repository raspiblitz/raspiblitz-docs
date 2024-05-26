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
    <div className={clsx("row row--4")}>
      <div style={{ width: "25%", padding: "0 20px" }}>
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
      <div style={{ width: "75%", padding: "0 20px" }}>
        <header className={styles.heroBanner}>
          <div className="container">
            <Heading as="h1" className="hero__title">
              {siteConfig.title}
            </Heading>
            <p className="hero__subtitle">{siteConfig.tagline}</p>
            <div className={styles.buttons}>
              <Link
                className="button button--secondary button--lg"
                to="/docs/intro"
              >
                To the tutorial
              </Link>
            </div>
          </div>
        </header>
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
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
