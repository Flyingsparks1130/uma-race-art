/* Exact outfit resolution for live results, bracket lineups and club builds. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.UmaRaceArt=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function resolve(catalog,selection,baseUrl=''){
    if(!catalog||!Array.isArray(catalog.assets)||!selection)return null;
    const card=selection.card_id??selection.cardId;
    const character=selection.character_id??selection.characterId;
    const costume=selection.costume_id??selection.costumeId;
    let candidates;
    if(card!=null){
      candidates=catalog.assets.filter(a=>String(a.card_id)===String(card));
      if(character!=null)candidates=candidates.filter(a=>String(a.character_id)===String(character));
      if(costume!=null)candidates=candidates.filter(a=>String(a.costume_id)===String(costume));
    }else if(character!=null&&costume!=null){
      candidates=catalog.assets.filter(a=>String(a.character_id)===String(character)&&String(a.costume_id)===String(costume));
    }else return null;
    if(candidates.length!==1)return null;
    const asset=candidates[0];
    if(asset.status!=='available'||!asset.path)return null;
    return {...asset,url:baseUrl?new URL(asset.path,baseUrl.endsWith('/')?baseUrl:baseUrl+'/').href:asset.path,
      alt:`${asset.character_name} — ${asset.outfit_name}`};
  }
  return {resolve};
});
