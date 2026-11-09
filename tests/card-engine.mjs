import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const E=require('../card-engine.js');
const basic=()=>E.deck({
  id:'deck-test',name:'Rechentest',mode:'without',exhaustion:'manual',
  cards:[
    {id:'a',title:'',text:'A',icon:'',color:'',frequency:'once',copies:1},
    {id:'b',title:'',text:'B',icon:'',color:'',frequency:'multiple',copies:5},
    {id:'c',title:'',text:'C',icon:'',color:'',frequency:'multiple',copies:2}
  ]
});
const stats=E.stats(basic());
assert.deepEqual(stats.rows.map(r=>r.originalChance),[12.5,62.5,25]);
assert.equal(stats.configured,8);
let deck=basic(),counts={a:0,b:0,c:0};
for(let i=0;i<8;i++){
  const x=E.draw(deck);assert.ok(x.card);counts[x.card.id]++;deck=x.deck;
  assert.equal(E.stats(deck).available,7-i);
  assert.ok(E.stats(deck).rows.every(r=>r.currentChance>=0&&r.currentChance<=100));
}
assert.deepEqual(counts,{a:1,b:5,c:2});
assert.equal(E.draw(deck).card,null);
assert.deepEqual(E.stats(E.store(JSON.parse(JSON.stringify({version:1,decks:[deck],pending:null})).decks[0]).rows.map(r=>r.available),[0,0,0]);
let d=basic();d.mode='with';
d=E.deck(d);
for(let i=0;i<200;i++) {
  const next=E.draw(d);assert.ok(next.card);
  d=next.deck;
  assert.equal(E.stats(d).rows.find(c=>c.id==='b').available,5);
}
assert.equal(E.stats(d).rows.find(c=>c.id==='a').available,0,'once card cannot reappear with replacement');
let auto=E.deck({...basic(),exhaustion:'auto'});
for(let i=0;i<8;i++)auto=E.draw(auto).deck;
const reshuffle=E.draw(auto);
assert.equal(reshuffle.reshuffled,true);
assert.equal(reshuffle.deck.state.round,2);
assert.equal(E.stats(reshuffle.deck).available,7);
let edited=basic(); edited=E.draw(edited,{getRandomValues:a=>{a[0]=1;return a;}}).deck;
let changed=JSON.parse(JSON.stringify(edited));changed.cards[1].copies=7;
let reconciled=E.reconcile(edited,changed);
assert.equal(reconciled.state.remaining.b,6,'edits preserve the consumed B copy');
changed=JSON.parse(JSON.stringify(reconciled));changed.cards[1].copies=1;
reconciled=E.reconcile(reconciled,changed);
assert.equal(reconciled.state.remaining.b,0,'reducing multiplicity never restores consumed copies');
let rejected=0;
assert.equal(E.uniformInt(3,{getRandomValues:a=>{a[0]=rejected++===0?4294967295:2;return a;}}),2);
assert.equal(rejected,2,'rejection sampling must retry out-of-range 32-bit values');
for(const [mutation,error] of [
  [d=>{d.cards[1].copies=-1;},/Multiplikator/],
  [d=>{d.cards[1].copies=1.5;},/Multiplikator/],
  [d=>{d.cards[1].text='<script>'.repeat(200);},/Kartentext/],
  [d=>{d.cards.push({...d.cards[0]});},/Doppelte/],
  [d=>{d.state.remaining.a=9;},/Vorrat/]
]){
  const bad=JSON.parse(JSON.stringify(basic()));mutation(bad);
  assert.throws(()=>E.deck(bad),error);
}
let seed=0x12345678;
const random={getRandomValues:a=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;a[0]=seed>>>0;return a;}};
const distribution={a:0,b:0,c:0};
const N=48000;
for(let i=0;i<N;i++)distribution[E.draw(basic(),random).card.id]++;
for(const [id,target] of Object.entries({a:.125,b:.625,c:.25})){
  const observed=distribution[id]/N;
  const sigma=Math.sqrt(target*(1-target)/N);
  assert.ok(Math.abs(observed-target)<5*sigma,id+': '+observed+' outside five sigma');
}
const small=E.deck({...basic(),cards:[basic().cards[0]]});
assert.equal(E.draw(small).card.id,'a');
assert.equal(E.draw(E.draw(small).deck).card,null);
const extreme=E.deck({...basic(),cards:[basic().cards[0],{...basic().cards[1],copies:1000}]});
assert.equal(E.stats(extreme).configured,1001);
console.log('PASS: finite draw, multiplier probabilities, no replacement, with replacement, once-only, auto reset, validation, persistence, unbiased RNG and seeded statistics.');
