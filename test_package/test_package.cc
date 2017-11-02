#include <stdio.h>
#include <graphviz/gvc.h>

int main()
{
	GVC_t *c = gvContext();
	if (!c)
	{
		printf("Couldn't initialize Graphviz.\n");
		return -1;
	}

	printf("Successfully initialized Graphviz.  Version [%s], build date [%s].\n", gvcVersion(c), gvcBuildDate(c));

	gvFreeContext(c);
	return 0;
}
