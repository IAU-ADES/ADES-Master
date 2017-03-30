
#include <ades.h>


static void usage(const char *name) {
    printf("Usage: %s [options] xmlfile\n", name);
    printf("      --param name value : pass a (parameter,value) pair\n");

}




int
main(int argc, char **argv) {
	int i;
	const char *params[16 + 1];
	int nbparams = 0;

	if (argc <= 0) {

		usage(argv[0]);
		return(1);
	}
	

 for (i = 1; i < argc; i++) {
        if (argv[i][0] != '-')
            break;
	if ((!strcmp(argv[i], "-param")) ||
                   (!strcmp(argv[i], "--param"))) {
		i++;
		params[nbparams++] = argv[i++];
		params[nbparams++] = argv[i];
		if (nbparams >= 16) {
			fprintf(stderr, "too many params\n");
			return (1);
		}
        }  else {
            fprintf(stderr, "Unknown option %s\n", argv[i]);
            usage(argv[0]);
            return (1);
        }
    }

	params[nbparams] = NULL;

	for (i = 0; i<nbparams; i++) {
		printf("params[%d] = %s\n", i, params[i]);
	}

	testRegularizeWhiteSpace(NULL);
	testRegularizeWhiteSpace(BAD_CAST "");
	testRegularizeWhiteSpace(BAD_CAST " ");
	testRegularizeWhiteSpace(BAD_CAST "    ");
	testRegularizeWhiteSpace(BAD_CAST "a   ");
	testRegularizeWhiteSpace(BAD_CAST " a  ");
	testRegularizeWhiteSpace(BAD_CAST "   a");
	testRegularizeWhiteSpace(BAD_CAST " a   a  ");
	testRegularizeWhiteSpace(BAD_CAST "a   a  ");
	testRegularizeWhiteSpace(BAD_CAST " a   a");
	testRegularizeWhiteSpace(BAD_CAST "a");
	

	testApplyPadding(BAD_CAST "This is a test", 20, 'L', 0);
	testApplyPadding(BAD_CAST "This is a test", 20, 'R', 0);
	testApplyPadding(BAD_CAST "This is a test", 20, 'C', 0);
	testApplyPadding(BAD_CAST "This is a test", 21, 'C', 0);
	testApplyPadding(BAD_CAST "This is a test", 22, 'C', 0);
	testApplyPadding(BAD_CAST "This is a test", 5, 'L', 0);
	testApplyPadding(BAD_CAST "This is a test", 5, 'R', 0);
	testApplyPadding(BAD_CAST "This is a test", 5, 'C', 0);
	testApplyPadding(BAD_CAST "43.12", 20, 'D' , 3);
	testApplyPadding(BAD_CAST "43.12234324", 25, 'D' , 8);
	testApplyPadding(BAD_CAST "43.12234324", 10, 'D' , 8);

	testApplyPadding(BAD_CAST "123.4567890123", 10, 'D', 1);
	testApplyPadding(BAD_CAST "123.4567890123", 10, 'D', 6);
	testApplyPadding(BAD_CAST ".333", 10, 'D', 1);
	testApplyPadding(BAD_CAST "333", 10, 'D', 1);
	testApplyPadding(BAD_CAST "333.", 10, 'D', 1);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 1);
	testApplyPadding(BAD_CAST "333", 10, 'D', 5);
	testApplyPadding(BAD_CAST ".333", 10, 'D', 5);
	testApplyPadding(BAD_CAST "333.", 10, 'D', 5);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 5);
	testApplyPadding(BAD_CAST ".333", 10, 'D', 8);
	testApplyPadding(BAD_CAST "333", 10, 'D', 8);
	testApplyPadding(BAD_CAST "333.", 10, 'D', 8);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 8);
	testApplyPadding(BAD_CAST ".333.", 10, 'D', 9);
	testApplyPadding(BAD_CAST "333", 10, 'D', 9);
	testApplyPadding(BAD_CAST "333", 10, 'D', 9);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 9);
	testApplyPadding(BAD_CAST ".333", 10, 'D', 10);
	testApplyPadding(BAD_CAST "333", 10, 'D', 10);
	testApplyPadding(BAD_CAST "333.", 10, 'D', 10);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 10);
	testApplyPadding(BAD_CAST ".333", 10, 'D', 11);
	testApplyPadding(BAD_CAST "333", 10, 'D', 11);
	testApplyPadding(BAD_CAST "333.", 10, 'D', 11);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 11);
	testApplyPadding(BAD_CAST "333.45444", 10, 'D', 2);
	testApplyPadding(BAD_CAST "333.45444", 10, 'D', 2);
	testApplyPadding(BAD_CAST "333.45444", 10, 'D', 4);
	testApplyPadding(BAD_CAST "333.45444", 10, 'D', 5);
	testApplyPadding(BAD_CAST "333.45444", 10, 'D', 6);
	testApplyPadding(BAD_CAST "333.454440000", 10, 'L', 0);
	testApplyPadding(BAD_CAST "333.454440000", 10, 'R', 0);
	testApplyPadding(BAD_CAST "333.45444", 10, 'L', 0);
	testApplyPadding(BAD_CAST "333.45444", 10, 'R', 0);
	testApplyPadding(BAD_CAST "", 10, 'D', 5) ;

	return(0);

}

