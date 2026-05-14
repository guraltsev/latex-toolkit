<TeXmacs|2.1.5>

<style|<tuple|generic|preview-ref|number-long-article|smart-ref|comment>>

<\body>
  <\hide-preamble>
    Equation alignment environments:

    The environment "cases" is provided by AMS LaTeX but TeXmacs does not
    know about it

    <assign|cases|<macro|body|<math-table-base|<style-with|src-compact|none|<left|{><tformat|<cwith|1|-1|1|-1|cell-swell|<value|table-math-swell>>|<twith|table-min-cols|1>|<twith|table-max-cols|2>|<arg|body>><right|.>>>>>

    <assign|dcases|<macro|body|<math-table-base|<style-with|src-compact|none|<left|{><tformat|<cwith|1|-1|1|-1|cell-swell|<value|table-math-swell>>|<twith|table-min-cols|1>|<twith|table-max-cols|2>|<arg|body>><right|.>>>>>

    The "ltae" construct can be exported to LaTeX and is rendered as a
    left-top-aligned block of equations. This is very convenient for
    splitting multi-line equations

    <assign|ltae|<macro|body|<tabular*|<tformat|<twith|table-valign|T>|<twith|table-min-cols|1>|<twith|table-max-cols|1>|<cwith|1|-1|1|-1|cell-halign|l>|<cwith|1|-1|1|-1|cell-lsep|0ln>|<arg|body>>>>>

    \;

    \;

    Common macro defitions

    Fonts

    calligraphic math

    <assign|mc|<macro|1|<with|math-font|cal|<arg|1>>>>

    fraktur math

    <assign|mf|<macro|1|<with|math-font|Euler|<arg|1>>>>

    blackboard math

    <assign|mbb|<macro|1|<with|font|Bbb*|<arg|1>>>>

    boldface math

    <assign|mb|<macro|1|<with|font-series|bold|<arg|1>>>>

    script math

    <assign|ms|<macro|1|<with|math-font|cal*|<arg|1>>>>

    roman math

    <assign|mrm|<macro|1|<math-up|<arg|1>>>>

    Noteworthy sets

    naturals

    <assign|N|<macro|\<bbb-N\>>>

    integers

    <assign|Z|<macro|\<bbb-Z\>>>

    rationals

    <assign|Q|<macro|\<bbb-Q\>>>

    reals

    <assign|R|<macro|\<bbb-R\>>>

    complex numbers

    <assign|C|<macro|\<bbb-C\>>>

    Function spaces / sets

    Schwarz space

    <assign|Sch|<macro|<ms|S>>>

    Borel functions/sets

    <assign|Bor|<macro|<ms|B>>>

    Lipschitz functions

    <assign|Lip|<macro|<math-up|Lip>>>

    locally (e.g. $L^{1}_{\\loc}$)

    <assign|loc|<macro|<math-up|loc>>>

    Linear algebra

    bounded linear maps

    <assign|Lin|<macro|<math-up|Lin>>>

    endomorphisms

    <assign|End|<macro|<math-up|End>>>

    homomorphism

    <assign|Hom|<macro|<math-up|Hom>>>

    linear group

    <assign|Gl|<macro|<math-up|Gl>>>

    special linear group

    <assign|Sl|<macro|<math-up|Sl>>>

    special unitary group

    <assign|SU|<macro|<math-up|SU>>>

    identity operator

    <assign|Id|<macro|<math-up|id>>>

    adjoint map

    <assign|Ad|<macro|<math-up|Ad>>>

    tangent adjoint map

    <assign|ad|<macro|<math-up|ad>>>

    rank

    <assign|rk|<macro|<math-up|rk>>>

    trace

    <assign|tr|<macro|<math-up|tr>>>

    Point set topology / metric spaces

    diameter

    <assign|diam|<macro|<math-up|diam>>>

    distance

    <assign|dist|<macro|<math-up|dist>>>

    support

    <assign|spt|<macro|<math-up|spt>>>

    Left/right -hand-side

    left-hand side of equtation

    <assign|LHS|<macro|1|<math-up|LHS><arg|1>>>

    right-hand side of equtation

    <assign|RHS|<macro|1|<math-up|RHS><arg|1>>>

    Miscellaneous math

    assignment

    <assign|eqdef|<macro|\<assign\>>>

    <assign|eqd|<macro|\<assign\>>>

    d of the differential

    <assign|dd|<macro|<math-up|\<mathd\>>>>

    such that

    <assign|st|<macro|<space|0.2spc>\<suchthat\><space|0.2spc>>>

    mapping e.g. $f \\of A \\to B$

    <assign|of|<macro|<space|0.2spc>\<suchthat\><space|0.2spc>>>

    Fourier transform operator

    <assign|Fourier|<macro|<compound|mf|F>>>

    Fourier transform symbol

    <assign|FT|<macro|body|<wide|<arg|body>|^>>>

    principle value

    <assign|pv|<macro|<math-up|p.v.>>>

    expectation

    <assign|E|<macro|\<bbb-E\>>>

    probability

    <assign|P|<macro|\<bbb-P\>>>

    torus

    <assign|T|<macro|\<bbb-T\>>>

    restriction to a domain

    <assign|restriction|<macro|1|<move|<left|lvert>|0pt|-3pt><rsub|<arg|1>>>>

    characteristic function

    <assign|1|<macro|<mbb|1>>>

    sign function

    <assign|sgn|<macro|<math-up|sgn>>>

    Symmetries

    modulation

    <assign|Mod|<macro|<math-up|Mod>>>

    translation

    <assign|Tr|<macro|<math-up|Tr>>>

    dilation

    <assign|Dil|<macro|<math-up|Dil>>>

    emb

    <assign|Em|<macro|<compound|ms|E>>>

    \;

    Chapter and Section numbering

    Table of Contents depth: Stop at sections (do not include subsections)

    <assign|subsubsection-toc|<macro|name|>>

    Chapter numbering

    <assign|chapter-nr|0>

    Section numbering

    <assign|section-nr|0>

    LLM helpers

    <assign|toLLM|<macro|body|<\wide-tabular>
      <tformat|<cwith|1|1|1|1|cell-background|pastel
      magenta>|<table|<row|<\cell>
        <arg|body>
      </cell>>>>
    </wide-tabular>>>

    <assign|fromLLM|<macro|body|<\wide-tabular>
      <tformat|<cwith|1|1|1|1|cell-background|pastel
      cyan>|<table|<row|<\cell>
        <arg|body>
      </cell>>>>
    </wide-tabular>>>

    <assign|step|<macro|body|<with|font-series|bold|<arg|body>>>>
  </hide-preamble>

  <\hide-preamble>
    <assign|C|<macro|\<bbb-C\>>>

    <assign|R|<macro|\<bbb-R\>>>
  </hide-preamble>

  <\hide-preamble>
    <assign|C|<macro|\<bbb-C\>>>

    <assign|R|<macro|\<bbb-R\>>>
  </hide-preamble>

  <\hide-preamble>
    <assign|C|<macro|\<bbb-C\>>>

    <assign|R|<macro|\<bbb-R\>>>
  </hide-preamble>

  Aligned t version:

  <\equation*>
    <around|\||<Em><rsub|\<psi\>><around|[|f|]><around|(|x,t|)>|\|><aligned|t|<tformat|<table|<row|<cell|>|<cell|\<le\><around|\<\|\|\>|f|\<\|\|\>><rsub|<wide|\<cal-C\>|\<dot\>><rsup|\<alpha\>><around|(|<R><rsup|d>|)>>*t<rsup|\<alpha\>>*<big|int><rsub|<R><rsup|d>><around|\||z|\|><rsup|\<alpha\>><around|\||\<psi\><rsub|<around|(|x,t|)>><around|(|z|)>|\|><space|0.17em><dd>z>>|<row|<cell|>|<cell|\<lesssim\><rsub|d,\<alpha\>,\<psi\>>t<rsup|\<alpha\>><around|\<\|\|\>|f|\<\|\|\>><rsub|<wide|\<cal-C\>|\<dot\>><rsup|\<alpha\>><around|(|<R><rsup|d>|)>>.>>>>>
  </equation*>

  LTAE version:

  <\equation*>
    <around|\||<Em><rsub|\<psi\>><around|[|f|]><around|(|x,t|)>|\|><ltae|<tformat|<table|<row|<cell|\<le\><around|\<\|\|\>|f|\<\|\|\>><rsub|<wide|\<cal-C\>|\<dot\>><rsup|\<alpha\>><around|(|<R><rsup|d>|)>>*t<rsup|\<alpha\>>*<big|int><rsub|<R><rsup|d>><around|\||z|\|><rsup|\<alpha\>><around|\||\<psi\><rsub|<around|(|x,t|)>><around|(|z|)>|\|><space|0.17em><dd>z>>|<row|<cell|\<lesssim\><rsub|d,\<alpha\>,\<psi\>>t<rsup|\<alpha\>><around|\<\|\|\>|f|\<\|\|\>><rsub|<wide|\<cal-C\>|\<dot\>><rsup|\<alpha\>><around|(|<R><rsup|d>|)>>.>>>>>
  </equation*>

  <\equation*>
    \;
  </equation*>
</body>

<\initial>
  <\collection>
    <associate|info-flag|short>
    <associate|page-medium|papyrus>
    <associate|preamble|false>
    <associate|src-close|compact>
    <associate|src-compact|inline>
    <associate|src-special|raw>
    <associate|src-style|scheme>
    <associate|stem-doc-id|A49E465C-6D81-4060-879F-5437086E26A0>
  </collection>
</initial>