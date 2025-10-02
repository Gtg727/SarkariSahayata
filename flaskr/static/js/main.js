// language selection small toast for demo
document.getElementById('langSelect')?.addEventListener('change', function(e){
  const lang = e.target.value;
  const el = document.createElement('div');
  el.className = 'alert alert-info position-fixed';
  el.style.top = '16px';
  el.style.right = '16px';
  el.style.zIndex = 9999;
  el.innerText = 'Language set to ' + lang;
  document.body.appendChild(el);
  setTimeout(()=>el.remove(),1500);
});
