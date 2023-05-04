import{a as c,j as t,r as i,D,E as R,H as L,F as E,C as $,L as O,t as b}from"./index-1201fba5.js";import{A as S}from"./axios-aaa1c0c0.js";const A=({idx:o,item:r})=>c("div",{className:"space-y-4 bg-gray-100 p-2 rounded-lg",children:[c("p",{className:"font-bold text-gray-800",children:["P",o+1]}),c("div",{className:"flex items-center justify-center  flex-col",children:[c("p",{className:"",children:["X: ",t("span",{className:"text-emerald-500 text-lg ml-1 font-bold",children:r.x.toFixed(2)})]}),c("p",{className:"",children:["Y: ",t("span",{className:"text-emerald-600 text-lg ml-1 font-bold",children:r.y.toFixed(2)})]})]})]},o);function M(o){const[r,n]=i.useState(JSON.parse(localStorage.getItem("draw-app"))||o);return[r,n]}function P(){const[o,r]=M([]),n=i.useRef(null);return[o,r,n]}const T=({imgSrc:o,points:r,finalPoints:n,setFinalPoints:g,setModalIsOpen:w})=>{const[u,y]=i.useState(null),[d,x,m]=P();function k(){const e=m.current,a=e.getContext("2d");a.clearRect(0,0,a.canvas.width,a.canvas.height);const s=new Image;s.src=o,s.onload=()=>y(s),N(e,a,s)}function N(e,a,s){let p=e.width,v=s==null?void 0:s.naturalWidth,h=s==null?void 0:s.naturalHeight,I=v/h,j=p/I;a.drawImage(s,0,0,p,j)}function C(){k();const e=()=>{g([]),x([])};return n.length>0||d.length>0?e():""}const F=(e,a,s)=>{var p=s.slice(0,4);g([...s]),a.lineCap="round",a.fillStyle="#FFFFFC",a.strokeStyle="lime",a.lineWidth=5,a.font="900 24px Courier";let v=4;N(e,a,u),a.beginPath(),a.moveTo(p[0].x,p[0].y),p.reverse().forEach(h=>{a.lineTo(h.x,h.y),a.fillText(`P${v--}`,h.x,h.y+20)}),a.fillStyle="rgba(226, 132, 19,0.5)",a.fill(),a.stroke()};function _(e){const a=m.current,s=a.getContext("2d"),p=a.getBoundingClientRect(),v=e.clientX-p.left,h=e.clientY-p.top,I={x:v,y:h};d.length<4?(f(s,v,h),x([...d,I])):(N(a,s,u),x([{x:v,y:h}]),g([]),f(s,v,h))}const f=(e,a,s)=>{e.fillStyle="lime",e.beginPath(),e.arc(a,s,10,0,2*Math.PI),e.fill()};i.useEffect(()=>{const e=new Image;e.src=o,e.onload=()=>y(e)},[]),i.useEffect(()=>{if(u&&m){const e=m.current,a=e.getContext("2d");N(e,a,u),r!=null&&r.coords&&x([...r.coords])}},[u,m]),i.useEffect(()=>{const e=m.current,a=e.getContext("2d");d.length>=4&&F(e,a,d)},[d]);const l=e=>{e.preventDefault(),w(!0)};return c("div",{className:"py-10 overflow-hidden",children:[t("div",{className:"absolute top-5 right-10  ",children:c("div",{className:"w-full flex items-center space-x-10",children:[c("button",{className:`text-white py-4 px-8 flex  items-center space-x-1 uppercase font-semibold rounded shadow  ${n&&n.length>0?"bg-emerald-500 hover:bg-emerald-800 hover:shadow-lg":"bg-gray-500 cursor-not-allowed"}`,disabled:n.length<=0,onClick:l,children:[t(D,{}),t("span",{children:"Save"})]}),c("button",{className:` text-white flex   items-center space-x-1 py-4 px-4 uppercase font-semibold rounded shadow  ${n&&n.length>0?"bg-gray-700 hover:bg-slate-500 hover:shadow-lg":"bg-gray-500 cursor-not-allowed"}`,disabled:n.length<=0,onClick:C,children:[t(R,{}),t("span",{children:"Refresh"})]})]})}),t("div",{className:"flex w-full justify-center item-center",children:t("canvas",{ref:m,width:(r==null?void 0:r.width)||1280,id:"canvasRef",height:(r==null?void 0:r.height)||720,className:"bg-gray-200 shadow-lg  filter drop-shadow-xl border-2 border-dark-bg rounded ",onClick:_})})]})},z=({handleSubmit:o,loading:r,input:n,cls:g,setInput:w})=>t("form",{onSubmit:o,children:c("div",{className:"flex flex-col md:flex-row  gap-5 md:gap-10  pt-5",children:[c("div",{className:"flex",children:[t("div",{className:"w-10 z-10 pl-1 text-center pointer-events-none flex items-center justify-center",children:t("svg",{fill:"none",className:"w-5 h-5 text-gray-500",stroke:"currentColor",strokeWidth:"1.5",viewBox:"0 0 24 24",xmlns:"http://www.w3.org/2000/svg","aria-hidden":"true",children:t("path",{strokeLinecap:"round",d:"M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25h-9A2.25 2.25 0 002.25 7.5v9a2.25 2.25 0 002.25 2.25z"})})}),t("input",{type:"text",disabled:r,value:n,onChange:u=>w(u.target.value),name:"rtsp",placeholder:"Enter camera source to update frame",autoComplete:"off",className:`  -ml-10 pl-10 pr-3 py-3 
          placeholder-gray-500 w-[28rem]   font-medium  text-lg   focus:outline-none   
          rounded-lg border-2 bg-core-widget  shadow-xl  filter drop-shadow-xl border-transparent outline-none focus:border-indigo-500 ${g}`})]}),t("button",{disabled:n===""||r,className:`py-3 px-8 rounded ${n!==""&&!r?"bg-indigo-500 hover:bg-indigo-700 focus:bg-indigo-700 text-white cursor-pointer":"bg-[#262442]  text-gray-600  cursor-not-allowed"} text-gray-100 font-semibold uppercase `,children:r?t(L,{name:"Please wait..."}):"Get Frame"})]})}),B=({loading:o})=>t("div",{style:{height:"calc(100vh - 100px)"},className:"flex space-y-2 flex-col items-center justify-center",children:o?t("p",{className:"text-xl md:text-5xl text-rose-500 font-medium",children:"Loading Frame..."}):c(E,{children:[t("p",{className:"text-xl uppercase md:text-5xl text-rose-500 font-medium",children:"Frame not found"}),t("p",{className:" text-gray-500 ",children:"Please enter camera source or begin processing to view the frame"})]})}),W=({setModalIsOpen:o,loading:r,children:n,title:g,handleAgreeButton:w})=>($(),c("div",{className:"min-w-screen h-screen animated fadeIn faster  fixed  left-0 top-0 flex justify-center items-center inset-0 z-[999] outline-none focus:outline-none bg-no-repeat bg-center bg-cover",id:"modal-id",children:[t("div",{className:"absolute bg-black opacity-70 inset-0 z-0"}),t("div",{className:"w-full  max-w-lg py-5 relative mx-auto my-auto rounded-xl shadow-lg  bg-[#1c1c28] ",children:c("div",{className:"",children:[c("div",{className:"text-center p-5 flex-auto justify-center space-y-7",children:[t("div",{children:t("h2",{className:"text-3xl font-bold text-[#ff3b3b] py-4 ",children:g})}),t("hr",{className:"w-full border-[#28293d]"}),n,t("hr",{className:"w-full border-[#28293d]"})]}),c("div",{className:"p-3  mt-2 text-center space-x-4 md:block",children:[t("button",{disabled:r,onClick:w,className:` ${r?"bg-dark-bg  text-gray-400  border-dark-bg  hover:bg-[#18172a] cursor-not-allowed":"bg-indigo-500 hover:bg-indigo-700 border-indigo-500 focus:bg-indigo-700 text-white cursor-pointer"} font-semibold rounded-full  uppercase leading-none  border-2  focus:outline-none hover:shadow-lg      px-5 py-2 tracking-wider  ease-in-out duration-300`,children:r?t(O,{name:"Please Wait..."}):t("div",{className:"font-bold",children:"Agree"})}),t("button",{onClick:()=>o(!1),className:"mb-2 md:mb-0  px-5 py-2 text-sm shadow-sm font-medium tracking-wider border-2 border-gray-500 text-gray-500 rounded-full hover:shadow-lg hover:text-gray-900 hover:bg-gray-500",children:"Cancel"})]})]})})]})),H=()=>{const[o,r]=i.useState(""),[n,g]=i.useState([]),[w,u]=i.useState(!1),[y,d]=i.useState(!1),[x,m]=i.useState(""),[k,N]=i.useState([]),C=window.localStorage.getItem("accessToken");return i.useEffect(()=>{(async()=>{const l=new FormData;l.append("auth_token",C);try{const{data:e}=await S.post("/get_roi",l);g(e)}catch{}})()},[]),i.useEffect(()=>{(async()=>{d(!0),r("");const l=new FormData;l.append("auth_token",C),l.append("input",x);try{const{data:e}=await S.post("/get_frame",l);if(e.status_code===100){b.success(e.msg);const a=`data:image/jpg;base64,${e.frame}`;r(a),m("")}else b.error(e.msg);d(!1)}catch(e){b.error(e.message),d(!1)}})()},[]),c("div",{className:"relative",children:[t(z,{handleSubmit:async f=>{f.preventDefault(),d(!0),r("");const l=new FormData;l.append("auth_token",C),l.append("input",x||0);try{const{data:e}=await S.post("/get_frame",l);if(e.status_code===100){b.success(e.msg);const a=`data:image/jpg;base64,${e.frame}`;r(a),m("")}else b.error(e.msg);d(!1)}catch(e){b.error(e.message),d(!1)}},loading:y,input:x,setInput:m}),o===""?t(B,{loading:y}):t("div",{children:t(T,{imgSrc:o,points:n,setModalIsOpen:u,finalPoints:k,setFinalPoints:N})}),w?t(W,{loading:y,handleAgreeButton:async f=>{f.preventDefault(),d(!0);const l={coords:[...k],auth_token:C};try{const{data:e}=await S.post("/set_roi",l);d(!1),e.status_code===100?(b.success(e.msg),g(e),u(!1)):(b.error(e.msg),u(!1))}catch(e){b.error(e.message),u(!1),d(!1)}},setModalIsOpen:u,title:"Modal",children:t("div",{children:t("div",{className:" flex items-center  justify-center font-medium uppercase  text-gray-700 space-x-5",children:k.map((f,l)=>t(A,{idx:l,item:f},l))})})}):null]})},G=()=>t("div",{className:"min-h-screen",children:t(H,{})});export{G as ROI,G as default};
