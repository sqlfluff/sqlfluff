// match_grammar = Delimited(
//         Ref("StatementSegment"),
//         delimiter=AnyNumberOf(Ref("DelimiterGrammar"), min_times=1),
//         allow_gaps=True,
//         allow_trailing=True,
//     )

pub fn file_segment(tokens: Vec<Token>) -> Segment {

    // match_grammar:
    //     Delimited(
    //         Ref("StatementSegment"),
    //         delimiter=AnyNumberOf(Ref("DelimiterGrammar"), min_times=1),
    //         allow_gaps=True,
    //         allow_trailing=True,
    //     )

}
