"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[5381],{8165:(e,i,t)=>{t.r(i),t.d(i,{assets:()=>l,contentTitle:()=>a,default:()=>c,frontMatter:()=>n,metadata:()=>r,toc:()=>h});var o=t(5893),s=t(1151);const n={sidebar_position:3},a="Final Steps",r={id:"setup/software-setup/finalize",title:"Final Steps",description:"Time to finish up the setup.",source:"@site/docs/setup/software-setup/3_finalize.md",sourceDirName:"setup/software-setup",slug:"/setup/software-setup/finalize",permalink:"/raspiblitz-docs/docs/setup/software-setup/finalize",draft:!1,unlisted:!1,editUrl:"https://github.com/fusion44/raspiblitz/tree/main/docs/docs/setup/software-setup/3_finalize.md",tags:[],version:"current",sidebarPosition:3,frontMatter:{sidebar_position:3},sidebar:"blitzSidebar",previous:{title:"Basic Setup",permalink:"/raspiblitz-docs/docs/setup/software-setup/basic"},next:{title:"RaspiBlitz Usage",permalink:"/raspiblitz-docs/docs/category/raspiblitz-usage"}},l={},h=[{value:"Final Setup",id:"final-setup",level:3},{value:"1. SYNC - Self validate all Blocks",id:"1-sync---self-validate-all-blocks",level:4},{value:"2. COPY - Copy from Laptop or another RaspiBlitz over Local Network",id:"2-copy---copy-from-laptop-or-another-raspiblitz-over-local-network",level:4}];function d(e){const i={a:"a",admonition:"admonition",code:"code",em:"em",h1:"h1",h3:"h3",h4:"h4",img:"img",mdxAdmonitionTitle:"mdxAdmonitionTitle",p:"p",strong:"strong",...(0,s.a)(),...e.components};return(0,o.jsxs)(o.Fragment,{children:[(0,o.jsx)(i.h1,{id:"final-steps",children:"Final Steps"}),"\n",(0,o.jsx)(i.p,{children:"Time to finish up the setup."}),"\n",(0,o.jsx)(i.p,{children:"Finally you have to set 3 passwords called A, B & C.\nFor each password please choose unique, single strings, without spaces and special characters, that are at least 8 chars long."}),"\n",(0,o.jsx)(i.p,{children:(0,o.jsx)(i.img,{alt:"SSH2",src:t(4264).Z+"",width:"401",height:"300"})}),"\n",(0,o.jsxs)(i.p,{children:["You can use this ",(0,o.jsx)(i.a,{href:"https://github.com/rootzoll/raspiblitz/raw/v1.7/home.admin/assets/RaspiBlitzRecoverySheet.pdf",children:"RaspiBlitz Recovery Sheet (PDF)"})," to write those passwords down for safe storage and also use it later on for your Seed Words."]}),"\n",(0,o.jsx)(i.p,{children:(0,o.jsx)(i.em,{children:(0,o.jsx)(i.strong,{children:"TODO: Not sure about the info boxes. They feel like they are too prominent and detract from the actual content"})})}),"\n",(0,o.jsxs)(i.admonition,{type:"info",children:[(0,o.jsx)(i.mdxAdmonitionTitle,{}),(0,o.jsxs)(i.p,{children:["The password A,B,C idea is based on the ",(0,o.jsx)(i.a,{href:"https://raspibolt.org/guide/raspberry-pi/preparations.html#write-down-your-passwords",children:"RaspiBolt Guide Preparations"})," - check out for more background."]})]}),"\n",(0,o.jsx)(i.p,{children:"First, password A is requested - this is the password which will be used for SSH login and it's also set for the existing users: admin, root, bitcoin & pi."}),"\n",(0,o.jsxs)(i.admonition,{type:"info",children:[(0,o.jsx)(i.mdxAdmonitionTitle,{}),(0,o.jsx)(i.p,{children:"The bitcoin and lightning services will later run in the background (as daemon) and use the separate user \u201cbitcoin\u201d for security reasons.\nThis user does not have admin rights and cannot change the system configuration."})]}),"\n",(0,o.jsx)(i.p,{children:"Then enter password B - this is internally used for the bitcoin RPC interface.\nIt is also used as login for additional apps like the RTL-WebGUI or the Blockexplorer."}),"\n",(0,o.jsx)(i.p,{children:'And finally enter password C - this is used to encrypt/lock the lightning wallet on the hard drive/SSD and is used by LND.\nEvery time a lightning node is started/rebooted LND needs load the wallet into memory to work with and ask you for password C to "unlock" the wallet.'}),"\n",(0,o.jsx)(i.admonition,{type:"info",children:(0,o.jsx)(i.p,{children:"In the early RaspiBlitz versions there was also an additional password D, that is no longer in use."})}),"\n",(0,o.jsx)(i.p,{children:"After this the setup process will need some time to set everything up - just wait until it's finished.\nThis can take from 10 to 30 minutes:"}),"\n",(0,o.jsx)(i.p,{children:(0,o.jsx)(i.img,{alt:"SSH4",src:t(2655).Z+"",width:"308",height:"188"})}),"\n",(0,o.jsx)(i.h3,{id:"final-setup",children:"Final Setup"}),"\n",(0,o.jsxs)(i.p,{children:['Once the basic setup has completed your lightning node will be setup & your lightning wallet will be created for you.\nAs part of this process you will be presented with your lightning node "seed words" which you ',(0,o.jsx)(i.em,{children:"MUST"})," write down on paper (or engrave into steel) and store in a secure location.\nYou will need to confirm that you wrote the seed words down before you can continue."]}),"\n",(0,o.jsx)(i.p,{children:(0,o.jsx)(i.img,{alt:"SSH4",src:t(8928).Z+"",width:"560",height:"262"})}),"\n",(0,o.jsx)(i.p,{children:"WRITE YOUR SEED WORDS DOWN before you continue - you will need them to recover funds in case of failing hardware etc.\nIf you just want to try/experiment with the RaspiBlitz, at least take a photo of the seed words with your smartphone, so you have something just in case.\nIf you plan to keep your RaspiBlitz running store this word list offline or in a password safe."}),"\n",(0,o.jsxs)(i.p,{children:["You can use this ",(0,o.jsx)(i.a,{href:"https://github.com/rootzoll/raspiblitz/raw/v1.7/home.admin/assets/RaspiBlitzRecoverySheet.pdf",children:"RaspiBlitz Recovery Sheet (PDF)"})," to write down your seed words for safe storage."]}),"\n",(0,o.jsx)(i.p,{children:"If you don't have a full copy of the blockchain pre-synced/validated on your hard drive/SSD then you will now be asked how you want to get your copy of the blockchain.\nThere are two basic options :"}),"\n",(0,o.jsx)(i.p,{children:(0,o.jsx)(i.img,{alt:"SSH4",src:t(1972).Z+"",width:"466",height:"252"})}),"\n",(0,o.jsx)(i.h4,{id:"1-sync---self-validate-all-blocks",children:"1. SYNC - Self validate all Blocks"}),"\n",(0,o.jsxs)(i.p,{children:["For the new RaspberryPi 4 (with SSD & min 2GB RAM) this is the best way to go.\nIt will take around 3-6 days to sync & validate directly with the bitcoin network.\nWith this option, you have done it the original ",(0,o.jsx)(i.code,{children:"don't trust, verify"})," way."]}),"\n",(0,o.jsx)(i.admonition,{type:"info",children:(0,o.jsx)(i.p,{children:"For the old RaspberryPi 3 this is not recommended.\nA RaspberryPi 3 has a very low power CPU and syncing+validating the blockchain directly with the peer2peer network can take multiple weeks - that's why for a RP3 you should choose the COPY option ._"})}),"\n",(0,o.jsx)(i.h4,{id:"2-copy---copy-from-laptop-or-another-raspiblitz-over-local-network",children:"2. COPY - Copy from Laptop or another RaspiBlitz over Local Network"}),"\n",(0,o.jsxs)(i.p,{children:["If you have a friend that is already running a synced RaspiBlitz or you have a laptop with enough free space on the hard drive that can download & validate the Blockchain much faster you can also choose the ",(0,o.jsx)(i.code,{children:"COPY"})," option.\nYou can then delete existing blockchain your RaspiBlitz already started syncing for you"]}),"\n",(0,o.jsx)(i.p,{children:(0,o.jsx)(i.img,{alt:"SSH4",src:t(4482).Z+"",width:"449",height:"268"})}),"\n",(0,o.jsxs)(i.p,{children:["To copy from another RaspiBlitz choose ",(0,o.jsx)(i.code,{children:"BLITZ"})," and follow the instructions.\nKnow that the other Blitz will be offline to the lightning network during the copy that will take multiple hours."]}),"\n",(0,o.jsxs)(i.p,{children:["To copy from your laptop/computer (",(0,o.jsx)(i.code,{children:"WINDOWS"}),", ",(0,o.jsx)(i.code,{children:"MACOS"})," & ",(0,o.jsx)(i.code,{children:"LINUX"})," options) you first need to download & validate the blockchain on your own computer/laptop.\nTo do so, install latest bitcoin-core (0.18.1 or higher) from ",(0,o.jsx)(i.a,{href:"https://bitcoin.org/en/download",children:"bitcoin.org"})," and keep it running until the blockchain is synced (will need around 400 GB).\nThen under the ",(0,o.jsx)(i.code,{children:"COPY"})," option choose the Operating System.\nThe copy will be done over the local network by SCP (SSH file transfer) - follow the instructions given in the dialogues.\nIt's advised to keep a backup of Bitcoin Core & the blockchain data directory on your laptop/computer in case you need to re-setup the RaspiBlitz."]}),"\n",(0,o.jsxs)(i.p,{children:["More details: ",(0,o.jsx)(i.a,{href:"/raspiblitz-docs/docs/faq/#i-have-the-full-blockchain-on-another-storage-how-do-i-copy-it-to-the-raspiblitz",children:"I have the full blockchain on another computer. How do I copy it to the RaspiBlitz?"})]}),"\n",(0,o.jsxs)(i.p,{children:["If you don't have the Bitcoin blockchain already on another laptop or RaspiBlitz simply choose ",(0,o.jsx)(i.code,{children:"SELFSYNC"}),"."]}),"\n",(0,o.jsxs)(i.p,{children:["And hooray ",":D"," Your RaspiBlitz is ready to go! Welcome new node operator."]}),"\n",(0,o.jsx)(i.p,{children:(0,o.jsx)(i.img,{alt:"SSH4",src:t(3923).Z+"",width:"475",height:"252"})}),"\n",(0,o.jsx)(i.p,{children:"If you hit OK, the RaspiBlitz will go into a final reboot."}),"\n",(0,o.jsx)(i.p,{children:(0,o.jsx)(i.img,{alt:"SSH5",src:t(6739).Z+"",width:"521",height:"155"})}),"\n",(0,o.jsx)(i.p,{children:"Just wait a bit and then the SSH command to login again.\nLogging in via SSH requires password A that you setup earlier."}),"\n",(0,o.jsx)(i.p,{children:(0,o.jsx)(i.img,{alt:"SSH5",src:t(3172).Z+"",width:"318",height:"162"})}),"\n",(0,o.jsxs)(i.p,{children:["If you run LND you will be asked to unlock your wallet - this requires password C.\nThere is an option to activate auto-unlock of LND if you prefer, this can be found under ",(0,o.jsx)(i.code,{children:"SETTINGS"})," in the main menu."]}),"\n",(0,o.jsx)(i.p,{children:(0,o.jsx)(i.img,{alt:"SSH5",src:t(2757).Z+"",width:"346",height:"147"})}),"\n",(0,o.jsx)(i.p,{children:"Your RaspiBlitz might need quite some time to sync and validate the blockchain -- this can be multiple days.\nIn the beginning you might see fast progress but this gets slower later on as historical blocks start to get fuller.\nYour RaspberryPi CPU will likely get quite hot during initial sync.\nHowever this is OK as the RaspberryPi has its own protection against overheating and will ensure the CPU doesn't critically overheat."})]})}function c(e={}){const{wrapper:i}={...(0,s.a)(),...e.components};return i?(0,o.jsx)(i,{...e,children:(0,o.jsx)(d,{...e})}):d(e)}},4264:(e,i,t)=>{t.d(i,{Z:()=>o});const o=t.p+"assets/images/ssh2-passwords-2d952b7877d7a2e4152d2f00eddc84dd.png"},1972:(e,i,t)=>{t.d(i,{Z:()=>o});const o=t.p+"assets/images/ssh4-blockchain-552883d28282b8706f9e5b1c44ab75ee.png"},4482:(e,i,t)=>{t.d(i,{Z:()=>o});const o=t.p+"assets/images/ssh4-copy-cd052a867d8b6ecbfd129e16b2505af3.png"},3923:(e,i,t)=>{t.d(i,{Z:()=>o});const o=t.p+"assets/images/ssh4-done-8e8d4774e61b80628fe35cb102b2e89c.png"},2655:(e,i,t)=>{t.d(i,{Z:()=>o});const o=t.p+"assets/images/ssh4-scripts-fbca49fd7468bf02b31adc1968d1c33d.png"},8928:(e,i,t)=>{t.d(i,{Z:()=>o});const o=t.p+"assets/images/ssh4-seed-a268677d0ced3bc290e96741975734d9.png"},2757:(e,i,t)=>{t.d(i,{Z:()=>o});const o=t.p+"assets/images/ssh5-blocksync-807016ea6fd663211c79c937d744bc3a.png"},6739:(e,i,t)=>{t.d(i,{Z:()=>o});const o=t.p+"assets/images/ssh5-reboot-0b586ba62de079ef896ad9d1bbd9bb68.png"},3172:(e,i,t)=>{t.d(i,{Z:()=>o});const o="data:image/png;base64,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sl60UfvqHZjxL48//rihLLMbnn76afPBBx/MbjQ6vwoIJGL4DjroIHPFFVd48b3zzjvm4YcfNjNnzvQeE9zx1VdfmUsvvdT8+uuvwZ/rbd94443m3XffrfdbnC/F5iVOnGHH7L333ub+++83X3zxhenUqZPhJqX8nTt3Nj///HPYKfY3yv7888+bMWPG/OdhEbXPG2FgRynMGqrbQPSxN2+66Sbz1ltvxT7ed+Ctt95qXnjhBd9u/S4CeQKJGL5//vnH8OcLO+20kxk1apSZZ555fIcU/Ttew0cffVT0eUnkJSwTiy22mJk+fbp5//337e7a2lprBBdccEHTvHnzsFPsb+uvv74577zzDPksDFH7Co8N+14Ks4bqNiwd/SYCWSMQa3CjXJnG2znppJNsdNzwl112Wb2o6/7+24yc9dT+7rvvzHzzzWd23313s+qqq9rjOP+MM86wzZl11lnHnHzyydaYfPbZZ7YZjOFzT3zO+fHHH81pp51m07zmmmvseeutt545JXfelzlPypeXadOmec+rmWMO48vnzjvvXK88wS9LLLGE+frrr80cufMXXnhhM3nyZLPGGmuYRRdd1B5GM/7mm282L730ks33/PPPb/r06WO9w2A8xWwzKHXxxReb1157zabbs2dP0717d0P5fMwWWmihYpKodywe9+WXX27jx9D37t3bdOnSxR6DwbztttvMI488Ysu31FJLmR49euT3u4jwYqnjFVdc0Rx55JHGVwaOL6yHGTNmuGj0KQKRBBLx+HwpcpMPGDDAbLTRRvbGKzxuWM443X333Wa11VYzxx13nDVm33//ff6wU0891TACdOihh5rnnnvOjB8/3hq6a6+91t5MEyZMMGzzN2XKFPPHH3+Yjz/+2Bo4dx7HPJ07LyovUeeRmYbymc9wYAPDx02Ncd5www1t/jDk/E646KKLzEMPPWTw4ig7/ZoY7tkJZ511lsGzJL7tt9/eGiX6NHk4+JiVmt4PP/xgTjzxROu9DhkyxKy55pqG9OlKIIwYMcI21TF2dFvsuOOO9sEWTA+PGGPHw+Hggw+2u3xlYGdhPTiWwTi1LQJhBFL1+GjactNzkzzxxBP18sONftddd5n+/fubvfbay+7D6wmGzTbbzN4Y/DZy5EiDV7jHHnvYP87p1atXvSbhhx9+aE8vPO+bb76xzWxfXlyaYefF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"},1151:(e,i,t)=>{t.d(i,{Z:()=>r,a:()=>a});var o=t(7294);const s={},n=o.createContext(s);function a(e){const i=o.useContext(n);return o.useMemo((function(){return"function"==typeof e?e(i):{...i,...e}}),[i,e])}function r(e){let i;return i=e.disableParentContext?"function"==typeof e.components?e.components(s):e.components||s:a(e.components),o.createElement(n.Provider,{value:i},e.children)}}}]);