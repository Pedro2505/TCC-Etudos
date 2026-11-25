/**
 * Texto em que toda menção a uma aba ("aba Resultados", "aba Testar ao vivo"…) vira link
 * para ela. Antes essas menções eram texto puro e não levavam a lugar nenhum.
 */
const ABAS = [
  ['Testar ao vivo', 'vivo'],
  ['Resultados do modelo', 'resultados'],
  ['Resultados', 'resultados'],
];

const PADRAO = new RegExp(`(aba (?:${ABAS.map(([n]) => n).join('|')}))`, 'g');

export default function ComLinks({ texto }) {
  return texto.split(PADRAO).map((parte, i) => {
    const aba = ABAS.find(([nome]) => parte === `aba ${nome}`);
    return aba
      ? <a key={i} className="link-aba" href={`#${aba[1]}`}>{parte}</a>
      : parte;
  });
}
