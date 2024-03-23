"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[7981],{5374:(e,t,o)=>{o.r(t),o.d(t,{assets:()=>l,contentTitle:()=>a,default:()=>c,frontMatter:()=>s,metadata:()=>r,toc:()=>d});var n=o(5893),i=o(1151);const s={},a="Migrate",r={id:"setup/migrate",title:"Migrate",description:"If you want to update from an older version of the RaspiBlitz software, you should follow these instructions",source:"@site/docs/setup/migrate.md",sourceDirName:"setup",slug:"/setup/migrate",permalink:"/docs/setup/migrate",draft:!1,unlisted:!1,editUrl:"https://github.com/fusion44/raspiblitz/tree/main/docs/docs/setup/migrate.md",tags:[],version:"current",frontMatter:{},sidebar:"blitzSidebar",previous:{title:"Final Steps",permalink:"/docs/setup/software-setup/finalize"},next:{title:"RaspiBlitz Usage",permalink:"/docs/category/raspiblitz-usage"}},l={},d=[{value:"Before you start migration",id:"before-you-start-migration",level:3},{value:"Instructions for Migration",id:"instructions-for-migration",level:2},{value:"Step by step instructions",id:"step-by-step-instructions",level:3},{value:"Troubleshooting without a connected display",id:"troubleshooting-without-a-connected-display",level:3}];function u(e){const t={a:"a",admonition:"admonition",h1:"h1",h2:"h2",h3:"h3",li:"li",p:"p",ul:"ul",...(0,i.a)(),...e.components};return(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(t.h1,{id:"migrate",children:"Migrate"}),"\n",(0,n.jsx)(t.admonition,{type:"info",children:(0,n.jsxs)(t.p,{children:["If you want to update from an older version of the RaspiBlitz software, you should follow ",(0,n.jsx)(t.a,{href:"/docs/setup/software-setup/basic",children:"these instructions"})]})}),"\n",(0,n.jsx)(t.p,{children:"Follow this guide only if you migrate from another node software like Umbrel or MyNode. If you run one of these, you basically have all the hardware needed and just need to change software. You don't need the LCD from the shopping list - RaspiBlitz can also run without an LCD."}),"\n",(0,n.jsx)(t.h3,{id:"before-you-start-migration",children:"Before you start migration"}),"\n",(0,n.jsxs)(t.ul,{children:["\n",(0,n.jsx)(t.li,{children:"if you have on-chain funds on your old node - make sure to have the backup seed words"}),"\n",(0,n.jsx)(t.li,{children:"if you have lightning channels open on your old node - make sure to have downloaded the latest Static Channel Backup file to your laptop"}),"\n"]}),"\n",(0,n.jsx)(t.p,{children:"Also be aware that at the moment RaspiBlitz can only transfer your blockchain and LND wallet data (including channels) over to RaspiBlitz. Any data/pairing of additional apps cannot be transferred and may get lost."}),"\n",(0,n.jsx)(t.h2,{id:"instructions-for-migration",children:"Instructions for Migration"}),"\n",(0,n.jsx)(t.h3,{id:"step-by-step-instructions",children:"Step by step instructions"}),"\n",(0,n.jsxs)(t.ul,{children:["\n",(0,n.jsx)(t.li,{children:"shutdown your old node"}),"\n",(0,n.jsx)(t.li,{children:"remove the SD card"}),"\n",(0,n.jsx)(t.li,{children:"download the latest RaspiBlitz sd card image & flash it to your sd card"}),"\n",(0,n.jsx)(t.li,{children:"if you want to use a HDMI monitor for status & progress, create a empty file called hdmi (without any ending) on the SD card while connected to your laptop"}),"\n",(0,n.jsx)(t.li,{children:"insert sd card, boot up & login by SSH"}),"\n"]}),"\n",(0,n.jsx)(t.p,{children:"Now RaspiBlitz should show you that old data from your node was detected and offer to do the migration for you."}),"\n",(0,n.jsxs)(t.ul,{children:["\n",(0,n.jsx)(t.li,{children:"If you choose to continue it will prepare the data & reboot."}),"\n",(0,n.jsx)(t.li,{children:"The RaspiBlitz recover/update mode is starting - that will take a while and finally reboot."}),"\n",(0,n.jsx)(t.li,{children:"Login by SSH as before and reset the passwords (FINAL RECOVERY LOGIN on LCD). Then a final reboot will happen."}),"\n",(0,n.jsx)(t.li,{children:"Login by SSH with your new password A & unlock LND wallet with password C. Now blockchain needs to catch up and then your RaspiBlitz should be ready and show you (under INFO) your on-chain & channel balance."}),"\n"]}),"\n",(0,n.jsx)(t.h3,{id:"troubleshooting-without-a-connected-display",children:"Troubleshooting without a connected display"}),"\n",(0,n.jsx)(t.p,{children:"If you don't have an LCD or HDMI monitor connected it might be a bit difficult to see what state your RaspiBlitz is in. Just (re-)try to login by SSH again after the reboots. It can take some time after a reboot before the operating system and SSH service is started, so just keep trying at intervals until successful."})]})}function c(e={}){const{wrapper:t}={...(0,i.a)(),...e.components};return t?(0,n.jsx)(t,{...e,children:(0,n.jsx)(u,{...e})}):u(e)}},1151:(e,t,o)=>{o.d(t,{Z:()=>r,a:()=>a});var n=o(7294);const i={},s=n.createContext(i);function a(e){const t=n.useContext(s);return n.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function r(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(i):e.components||i:a(e.components),n.createElement(s.Provider,{value:t},e.children)}}}]);