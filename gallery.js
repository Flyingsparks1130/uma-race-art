'use strict';
(async()=>{
const list=document.getElementById('gallery'),status=document.getElementById('status'),search=document.getElementById('search'),variants=document.getElementById('variants');
try{
  const response=await fetch('catalog.json');if(!response.ok)throw new Error('Catalog unavailable');
  const catalog=await response.json();
  const render=()=>{
    const query=search.value.trim().toLowerCase(),mode=variants.value;
    const assets=catalog.assets.filter(a=>(mode==='all'||(mode==='original'?a.outfit_id==='original':a.outfit_id!=='original'))&&[a.character_name,a.outfit_name,a.outfit_id,a.card_id,a.costume_id].join(' ').toLowerCase().includes(query));
    list.replaceChildren();
    for(const a of assets){
      const article=document.createElement('article'),figure=document.createElement('figure'),info=document.createElement('div');
      if(a.status==='available'){
        const image=document.createElement('img');image.src=a.path;image.alt=`${a.character_name} — ${a.outfit_name}`;image.loading='lazy';image.decoding='async';image.width=a.width;image.height=a.height;image.addEventListener('error',()=>{figure.textContent='Exact outfit image unavailable';});figure.append(image);
      }else figure.textContent='Exact outfit image unavailable';
      const title=document.createElement('h2');title.textContent=a.character_name;
      const outfit=document.createElement('p');outfit.textContent=a.outfit_name;
      const ids=document.createElement('small');ids.textContent=`Card ${a.card_id} · Costume ${a.costume_id}`;
      const dimensions=document.createElement('small');dimensions.textContent=a.status==='available'?`${a.width} × ${a.height} · Original PNG`:'Unavailable';
      const source=document.createElement('a');source.href=a.source_page;source.textContent='Source';source.target='_blank';source.rel='noopener';
      info.append(title,outfit,source,ids,dimensions);article.append(figure,info);list.append(article);
    }
    status.textContent=`${assets.length} of ${catalog.assets.length} outfit variants · Catalog updated ${catalog.updated}`;
  };
  search.addEventListener('input',render);variants.addEventListener('change',render);render();
}catch(error){status.textContent='The catalog could not be loaded. Serve this folder over HTTP and try again.';}
})();
