# Edge Cases Parser

List of chord edge cases or abnormalities encountered in [lluccardoner-melodyGPT-song-chords-text-1](https://huggingface.co/datasets/lluccardoner/melodyGPT-song-chords-text-1)

| **raw chord**      | **parsed chord**                      | **issue**                                 | **gravity** | **status**  | **commit**                               |
| ------------------ | ------------------------------------- | ----------------------------------------- | ----------- | ----------- | ---------------------------------------- |
| F#/-7b5            | C(q3:maj)(u:-7b5)                     | slash not tokenized                       | low/rare    | fixed       | 9481170a7a8b6fbdbbce09c19c999ad33ccbeb08 |
| G5/B5/A5/G5        | C(q3:maj)(e:5)/D                      | cluster                                   | high        | fixed       | e10070c76e0216b28f75950b9b3bf724413e1b96 |
| F/Bb-Bb-Eb-F/Bb-Bb | C(q3:m)/D                             | cluster                                   | high        | fixed       | e10070c76e0216b28f75950b9b3bf724413e1b96 |
| D5(PM)             | C(q3:maj)(e:5)                        | wrong quality?                            | high        | fixed       | c30530c985422a913a5de6ec7e94005a50524351 |
| D(Strum-once)      | C(q3:m)                               | wrong quality                             | high        | fixed       | c30530c985422a913a5de6ec7e94005a50524351 |
| C(Palm-mute)       | C(q3:m)                               | wrong quality                             | high        | fixed       | c30530c985422a913a5de6ec7e94005a50524351 |
| C(6X)              | C(q3:maj)(e:6)                        | wrong ext                                 | high        | fixed       | c30530c985422a913a5de6ec7e94005a50524351 |
| Cadd9(4x)          | C(q3:maj)(m:add4,add9)                | wrong add                                 | high        | fixed       | c30530c985422a913a5de6ec7e94005a50524351 |
| B7(x21000)         | C(q3:maj)(q7:m)(m:add2)               | wrong add                                 | high        | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| D6(2x)             | C(q3:maj)(m:add2)(e:6)                | wrong add                                 | high        | fixed       | c30530c985422a913a5de6ec7e94005a50524351 |
| G(x2)              | C(q3:maj)(m:add2)                     | wrong add                                 | high        | fixed       | c30530c985422a913a5de6ec7e94005a50524351 |
| Am(string2open)    | C(q3:m)(m:add2)                       | wrong add                                 | high        | fixed       | c30530c985422a913a5de6ec7e94005a50524351 |
| D5(XX0234)         | C(q3:maj)(m:add2,add4)(e:5)           | tab as ext                                | high        | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| Bm/D(XX0777)       | C(q3:m)/D                             | tab as ext                                | high        | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| F7(131233)         | C(q3:maj)(q7:m)(m:add2)(e:13)         | tab as ext                                | high        | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| E+(x02110)         | C(q3:maj)(q5:aug)(q7:m)(m:add2)(e:11) | tab as ext                                | high        | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| Db(no5)            | C(q3:maj)(e:5)                        | no5 is not 5                              | high        | fixed       | 70b1e9fae3f0e388e2a4e30288903062de464a30 |
| Ab(no5)            | C(q3:maj)(e:5)                        | no5 is not 5                              | high        | fixed       | 70b1e9fae3f0e388e2a4e30288903062de464a30 |
| Eb(no5)            | C(q3:maj)(e:5)                        | no5 is not 5                              | high        | fixed       | 70b1e9fae3f0e388e2a4e30288903062de464a30 |
| D9(s/c)            | C(q3:maj)(q7:m)(e:9)(u:c)             | string not cleaned                        | low         | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| G(s/c)             | C(q3:maj)(u:c)                        | string not cleaned                        | low         | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| A(s/c)             | C(q3:maj)(u:c)                        | string not cleaned                        | low         | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| G/B(once)          | C(q3:maj)/D                           | string not cleaned                        | low         | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| F#/Bb(Hold)        | C(q3:maj)/D                           | string not cleaned                        | low         | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| F#(hold)           | C(q3:maj)                             | string not cleaned                        | low         | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| A(chord)           | C(q3:maj)                             | string not cleaned                        | low         | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| Am(rasgueo)        | C(q3:m)                               | string not cleaned                        | low         | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| A(rasgueo)         | C(q3:maj)                             | string not cleaned                        | low         | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| B7(rasgueo)        | C(q3:maj)(q7:m)                       | string not cleaned                        | low         | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| A(x3)              | C(q3:maj)                             | repetition counter                        | low         | fixed       | 9bf87fc292a30e70c2d82d2b4296fb55ca6edc7e |
| Gsus2/maj7         | C(q3:sus2)(u:maj7)                    | quality lost                              | low         | left as is  |                                          |
| G7(4/9)            | G(q3:maj)(q7:m)(u:4/9)                | nesting, parenthesis doesn’t see / as sep | moderate    | to be fixed |                                          |
| E4(7/9)            | E(q3:maj)(m:add4)(u:7/9)              | nesting, parenthesis doesn’t see / as sep | moderate    | to be fixed |                                          |
| A7(9/13)           | A(q3:maj)(q7:m)(u:9/13)               | nesting, parenthesis doesn’t see / as sep | moderate    | to be fixed |                                          |
