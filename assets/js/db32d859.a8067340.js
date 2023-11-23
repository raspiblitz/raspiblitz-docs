"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[6653],{6564:(e,i,t)=>{t.r(i),t.d(i,{assets:()=>l,contentTitle:()=>a,default:()=>h,frontMatter:()=>r,metadata:()=>o,toc:()=>d});var n=t(5893),s=t(1151);const r={sidebar_position:2},a="Security Policy",o={id:"security",title:"Security Policy",description:"NOTE: This document is just a first draft and still under construction.",source:"@site/docs/security.md",sourceDirName:".",slug:"/security",permalink:"/raspiblitz-docs/docs/security",draft:!1,unlisted:!1,editUrl:"https://github.com/fusion44/raspiblitz/tree/main/docs/docs/security.md",tags:[],version:"current",sidebarPosition:2,frontMatter:{sidebar_position:2},sidebar:"blitzSidebar",previous:{title:"Intro",permalink:"/raspiblitz-docs/docs/intro"},next:{title:"RaspiBlitz Setup",permalink:"/raspiblitz-docs/docs/category/raspiblitz-setup"}},l={},d=[{value:"Minimal SD Card Build",id:"minimal-sd-card-build",level:2},{value:"Supported Versions",id:"supported-versions",level:2},{value:"Reporting a Vulnerability",id:"reporting-a-vulnerability",level:2},{value:"Lightning Wallet (default)",id:"lightning-wallet-default",level:2},{value:"Bitcoin Core Wallet (deactivated by default)",id:"bitcoin-core-wallet-deactivated-by-default",level:2}];function c(e){const i={a:"a",admonition:"admonition",code:"code",em:"em",h1:"h1",h2:"h2",li:"li",p:"p",pre:"pre",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",ul:"ul",...(0,s.a)(),...e.components};return(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(i.h1,{id:"security-policy",children:"Security Policy"}),"\n",(0,n.jsx)(i.admonition,{type:"info",children:(0,n.jsx)(i.p,{children:(0,n.jsx)(i.em,{children:"NOTE: This document is just a first draft and still under construction."})})}),"\n",(0,n.jsx)(i.p,{children:"Only use this software with funds you could afford to lose. Especially a lightning wallet that is a hot wallet, which has constant connection to the internet and can be target of exploitation."}),"\n",(0,n.jsx)(i.p,{children:"Just because the software is OpenSource does not mean its free of errors. Especially if you run additional apps, the RaspiBlitz team cannot review all the code of those external projects."}),"\n",(0,n.jsxs)(i.p,{children:['The software is provided "AS IS", without warranty of any kind. In no event shall the authors or copyright holders be liable for any claim, damages or other\nliability. ',(0,n.jsx)(i.a,{href:"https://github.com/fusion44/raspiblitz/blob/dev/LICENSE",children:"details on legal license"})]}),"\n",(0,n.jsx)(i.h2,{id:"minimal-sd-card-build",children:"Minimal SD Card Build"}),"\n",(0,n.jsxs)(i.p,{children:["To improve the UX for beginners & casual users we decided to preinstall & activate lots of features like LCD, API & WebUI of RaspiBlitz from the beginning and even preinstall/compile a selection of additional apps in the default ",(0,n.jsx)(i.code,{children:"fatpack"})," sd card image. This creates a bigger attack surface and more trusted dependencies on the security side. For more advanced users we also provide a ",(0,n.jsx)(i.code,{children:"minimal"})," sd card image in the download section - which aims to install just the basics and every else will be just installed/compiled on-demand - this is recommended for users (especially on updates) that already know what features they want/need from their RaspiBlitz to run it with the reduced attack surface. To create a minimal sd card yourself run the ",(0,n.jsx)(i.code,{children:"build_sdcard.sh"})," script with the options ",(0,n.jsx)(i.code,{children:"-f 0"})," (fatpack off) & ",(0,n.jsx)(i.code,{children:"-d headless"})," (to not preinstall external LCD drivers)."]}),"\n",(0,n.jsx)(i.h2,{id:"supported-versions",children:"Supported Versions"}),"\n",(0,n.jsx)(i.p,{children:"Updates are made only for the latest version."}),"\n",(0,n.jsxs)(i.p,{children:["Security patches can be done with ",(0,n.jsx)(i.code,{children:"MAINMENU > UPDATE > PATCH"})," for the current branch in the case of a high risk issue before next release."]}),"\n",(0,n.jsxs)(i.p,{children:["The latest version always have the ",(0,n.jsx)(i.code,{children:"latest"})," tag. To make sure you are using the latest version, run:"]}),"\n",(0,n.jsx)(i.pre,{children:(0,n.jsx)(i.code,{children:"curl -s https://api.github.com/repos/rootzoll/raspiblitz/releases/latest|grep tag_name|head -1|cut -d '\"' -f4\n"})}),"\n",(0,n.jsx)(i.h2,{id:"reporting-a-vulnerability",children:"Reporting a Vulnerability"}),"\n",(0,n.jsxs)(i.p,{children:["To report security issues send an email to ",(0,n.jsx)(i.a,{href:"mailto:christian@rotzoll.de",children:"christian@rotzoll.de"})," (not for support)."]}),"\n",(0,n.jsx)(i.p,{children:"The following keys may be used to communicate sensitive information to developers:"}),"\n",(0,n.jsxs)(i.table,{children:[(0,n.jsx)(i.thead,{children:(0,n.jsxs)(i.tr,{children:[(0,n.jsx)(i.th,{children:"Name"}),(0,n.jsx)(i.th,{children:"Fingerprint"}),(0,n.jsx)(i.th,{children:"64-bit"})]})}),(0,n.jsxs)(i.tbody,{children:[(0,n.jsxs)(i.tr,{children:[(0,n.jsx)(i.td,{children:"Rootzoll"}),(0,n.jsx)(i.td,{children:"92A7 46AE 33A3 C186 D014 BF5C 1C73 060C 7C17 6461"}),(0,n.jsx)(i.td,{children:"1C73 060C 7C17 6461"})]}),(0,n.jsxs)(i.tr,{children:[(0,n.jsx)(i.td,{children:"Openoms"}),(0,n.jsx)(i.td,{children:"13C6 88DB 5B9C 745D E4D2 E454 5BFB 7760 9B08 1B65"}),(0,n.jsx)(i.td,{children:"5BFB 7760 9B08 1B65"})]})]})]}),"\n",(0,n.jsx)(i.p,{children:"You can import a key by running the following command with that individual\u2019s fingerprint:"}),"\n",(0,n.jsx)(i.pre,{children:(0,n.jsx)(i.code,{children:"curl https://keybase.io/rootzoll/pgp_keys.asc | gpg --import\ncurl https://keybase.io/oms/pgp_keys.asc | gpg --import\n"})}),"\n",(0,n.jsx)(i.p,{children:"Ensure that you put quotes around fingerprints containing spaces if importing with other methods."}),"\n",(0,n.jsx)(i.h1,{id:"privacy-protection",children:"Privacy Protection"}),"\n",(0,n.jsxs)(i.p,{children:["When you call ",(0,n.jsx)(i.code,{children:"debug"})," on the command line you get basic system & services logs that can be used if you need to report details for support by other users. There is already a basic redaction of private data (nodeids, IPv4s, .onion-addresses, balances) for that debug report BUT always check the data you post in DMs or public before sending. If you find further private data that needs redaction, please report as an issue on the github repo."]}),"\n",(0,n.jsx)(i.h1,{id:"network-security",children:"Network Security"}),"\n",(0,n.jsxs)(i.ul,{children:["\n",(0,n.jsx)(i.li,{children:"Limit attack surface: Wi-fi and Bluetooth is disabled by default in the build script."}),"\n",(0,n.jsx)(i.li,{children:"Firewall: UFW is active and only specific ports are open, closing ports and removing hidden services when services are uninstalled."}),"\n",(0,n.jsx)(i.li,{children:"Password brute forcing protection: Fail-2-Ban is protecting the SSH login against brute-force-attacks."}),"\n"]}),"\n",(0,n.jsx)(i.h1,{id:"software-security",children:"Software security"}),"\n",(0,n.jsxs)(i.ul,{children:["\n",(0,n.jsxs)(i.li,{children:["\n",(0,n.jsxs)(i.p,{children:["The ",(0,n.jsx)(i.code,{children:"admin"})," (and the ",(0,n.jsx)(i.code,{children:"joinmarket"})," [optional]) users have passwordless sudo access to be able to perform installations and read password without much user interaction."]}),"\n"]}),"\n",(0,n.jsxs)(i.li,{children:["\n",(0,n.jsx)(i.p,{children:"Downloaded binaries and source code is verified with the authors' PGP keys by either:"}),"\n",(0,n.jsxs)(i.ul,{children:["\n",(0,n.jsx)(i.li,{children:"signed shasum files and checking the hash of each downloaded binary"}),"\n",(0,n.jsxs)(i.li,{children:["verifying the signature on the source code changes utilising the ",(0,n.jsx)(i.code,{children:"git verify-commit"})," or ",(0,n.jsx)(i.code,{children:"git verify-tag"})," commands"]}),"\n"]}),"\n"]}),"\n"]}),"\n",(0,n.jsx)(i.h1,{id:"physical-security",children:"Physical Security"}),"\n",(0,n.jsxs)(i.ul,{children:["\n",(0,n.jsx)(i.li,{children:"The lightning wallet and user interfaces are password protected by default so this has more privacy implications (in the case of physical theft) than security."}),"\n",(0,n.jsx)(i.li,{children:"Basic hardening measures are applied to all non-root systemd services"}),"\n",(0,n.jsx)(i.li,{children:"Optional log in through SSH using a hardware wallet."}),"\n",(0,n.jsx)(i.li,{children:"LUKS encryption would be welcome in the future."}),"\n"]}),"\n",(0,n.jsx)(i.h1,{id:"on-chain-funds",children:"On-chain Funds"}),"\n",(0,n.jsx)(i.p,{children:"Please keep in mind that there can be two different on-chain wallets on the RaspiBlitz:"}),"\n",(0,n.jsx)(i.h2,{id:"lightning-wallet-default",children:"Lightning Wallet (default)"}),"\n",(0,n.jsx)(i.p,{children:"The default is the on-chain lightning wallet - that's the wallet where you normally send your funds before opening a channel & where your funds return to when you close a channel. With the initial word seed you get during RaspiBlitz setup, you can get access again to this on-chain wallet. Keep the seed words secure in a off-line location."}),"\n",(0,n.jsx)(i.h2,{id:"bitcoin-core-wallet-deactivated-by-default",children:"Bitcoin Core Wallet (deactivated by default)"}),"\n",(0,n.jsx)(i.p,{children:"Beside lightning you have a Bitcoin core installed. Normally, Bitcoin core acts just as a blockchain informational service to the lightning wallet and its internal separate on-chain wallet is deactivated."}),"\n",(0,n.jsx)(i.p,{children:"Some apps (like Fully Noded or JoinMarket) activate the Bitcoin core wallet and use it for their own needs. This on-chain balance will not be reflected in the rest of the RaspiBlitz software and is NOT backed up by the seed words from the RaspiBlitz setup. If you make use of the Bitcoin core wallet please take care of these funds."}),"\n",(0,n.jsx)(i.h1,{id:"off-chain-funds-lightning-channels",children:"Off-chain Funds (Lightning Channels)"}),"\n",(0,n.jsxs)(i.p,{children:["Please note that there is no perfect backup concept for the funds in your lightning channels yet. We strongly recommend using the ",(0,n.jsx)(i.code,{children:"Static Channel Backup"})," provided by LND and consider off-line location backup of that file to have the best chances to recover Lightning funds in a case of recovering from a disaster."]}),"\n",(0,n.jsxs)(i.p,{children:["The C-lightning lightning.sqlite3 is replicated on the SDcard from the disk in real time. See more details in the ",(0,n.jsx)(i.a,{href:"faq/cl#backups",children:"Core Lightning FAQ"})]}),"\n",(0,n.jsxs)(i.p,{children:["For more practical information on this topic see: ",(0,n.jsx)(i.code,{children:"TODO: Backup Channel Funds README.md#backup-for-on-chain---channel-funds"})]})]})}function h(e={}){const{wrapper:i}={...(0,s.a)(),...e.components};return i?(0,n.jsx)(i,{...e,children:(0,n.jsx)(c,{...e})}):c(e)}},1151:(e,i,t)=>{t.d(i,{Z:()=>o,a:()=>a});var n=t(7294);const s={},r=n.createContext(s);function a(e){const i=n.useContext(r);return n.useMemo((function(){return"function"==typeof e?e(i):{...i,...e}}),[i,e])}function o(e){let i;return i=e.disableParentContext?"function"==typeof e.components?e.components(s):e.components||s:a(e.components),n.createElement(r.Provider,{value:i},e.children)}}}]);