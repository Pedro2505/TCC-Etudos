/**
 * Rola até logo acima da barra de abas, se a página estiver mais para baixo.
 *
 * Usa o marcador #topo-abas, e não a própria barra: a barra é sticky, e um
 * elemento sticky preso no topo informa a posição presa, não a original.
 */
export function rolarParaAbas(suave = false) {
  const marcador = document.getElementById('topo-abas');
  if (!marcador) return;
  const topo = marcador.getBoundingClientRect().top + window.scrollY;
  if (window.scrollY > topo) window.scrollTo({ top: topo, behavior: suave ? 'smooth' : 'auto' });
}
