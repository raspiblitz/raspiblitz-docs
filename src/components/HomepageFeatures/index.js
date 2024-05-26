import clsx from "clsx";
import Heading from "@theme/Heading";
import styles from "./styles.module.css";

const FeatureList = [
  {
    title: "Open Source",
    Svg: require("@site/static/img/undraw_docusaurus_mountain.svg").default,
    description: (
      <>
        The project is unapologetically open source under the MIT licence. This
        means that anyone can fork, modify and use the code to their heart's
        content.
      </>
    ),
  },
  {
    title: "Batteries Included",
    Svg: require("@site/static/img/undraw_docusaurus_tree.svg").default,
    description: (
      <>
        The RaspiBlitz includes a wide range of apps and tools that are widely
        used in the ecosystem. They can be turned on and off at the user's
        discretion.
      </>
    ),
  },
  {
    title: "Two Versions",
    Svg: require("@site/static/img/undraw_docusaurus_react.svg").default,
    description: (
      <>
        The RaspiBlitz is available in two versions: the "Minimal" edition
        prioritizes robust security features, while the "Fatpack" version offers
        more features at the cost of some security.{" "}
        <a href="./docs/security.html">Learn more</a>
      </>
    ),
  },
];

function Feature({ Svg, title, description }) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
